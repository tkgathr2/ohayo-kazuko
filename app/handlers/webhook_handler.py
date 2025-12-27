import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Request

from app.models import DepartureRecord
from app.services import judge_departure
from app.utils.logger import get_logger
from app.utils.validators import parse_time_string, validate_time_string


router = APIRouter()


def _get_services(request: Request):
    line_service = request.app.state.line_service
    sheet_service = request.app.state.sheet_service
    phone_service = request.app.state.phone_service
    return line_service, sheet_service, phone_service


@router.post("/webhook/line")
async def line_webhook(request: Request):
    line_service, sheet_service, phone_service = _get_services(request)
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")
    if not line_service.verify_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()
    events = payload.get("events", [])
    tz = ZoneInfo("Asia/Tokyo")
    logger = get_logger("webhook_handler")

    for event in events:
        event_type = event.get("type")
        if event_type == "postback":
            postback = event.get("postback", {})
            data_raw = postback.get("data", "{}")
            try:
                data = json.loads(data_raw)
            except json.JSONDecodeError:
                data = {}
            if data.get("action") != "departure_report":
                continue

            line_id = event.get("source", {}).get("userId")
            if not line_id:
                continue
            event_ts = event.get("timestamp")
            actual_time = datetime.fromtimestamp(event_ts / 1000, tz=tz) if event_ts else datetime.now(tz)

            today = actual_time.date()
            found = sheet_service.get_departure_record(today, line_id)
            if found:
                _, record = found
                if record.actual_departure_time:
                    await line_service.send_message(line_id, "既に出発報告済みです。")
                    continue
            else:
                cast_name = None
                for cast in sheet_service.get_casts():
                    if cast.line_id == line_id:
                        cast_name = cast.name
                        break
                if not cast_name:
                    await line_service.send_message(line_id, "登録情報が見つかりません。")
                    continue
                record = DepartureRecord(date=today, name=cast_name, line_id=line_id)

            if record.scheduled_departure_time is None:
                await line_service.send_message(line_id, "出発予定時間が未登録です。")
                continue

            status = judge_departure(actual_time, record.scheduled_departure_time, actual_time)
            record.actual_departure_time = actual_time
            record.departure_status = status
            sheet_service.upsert_departure_record(record)
            phone_service.cancel_phone_calls(line_id)
            await line_service.send_message(line_id, "出発報告を受け付けました。")

        if event_type == "message":
            message = event.get("message", {})
            if message.get("type") != "text":
                continue
            text = message.get("text", "").strip()
            if not validate_time_string(text):
                continue
            line_id = event.get("source", {}).get("userId")
            if not line_id:
                continue
            next_day = (datetime.now(tz) + timedelta(days=1)).date()
            time_value = parse_time_string(text)
            scheduled = datetime.combine(next_day, time_value, tzinfo=tz)

            cast_name = None
            for cast in sheet_service.get_casts():
                if cast.line_id == line_id:
                    cast_name = cast.name
                    break
            if not cast_name:
                await line_service.send_message(line_id, "登録情報が見つかりません。")
                continue
            record = DepartureRecord(
                date=next_day,
                name=cast_name,
                line_id=line_id,
                scheduled_departure_time=scheduled,
            )
            sheet_service.upsert_departure_record(record)
            await line_service.send_message(line_id, f"出発予定時間を{ text }で登録しました。")

    return {"status": "ok"}
