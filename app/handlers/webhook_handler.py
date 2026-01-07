"""LINE Webhook処理（起床報告、リマインド時刻設定対応）"""
import json
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Request

from app.models import DepartureRecord
from app.services.departure_service import judge_departure, judge_wakeup
from app.utils.logger import get_logger
from app.utils.validators import parse_time_string, validate_time_string


router = APIRouter()


def _get_services(request: Request):
    """リクエストからサービスと設定を取得"""
    line_service = request.app.state.line_service
    sheet_service = request.app.state.sheet_service
    phone_service = request.app.state.phone_service
    settings = request.app.state.settings
    return line_service, sheet_service, phone_service, settings


@router.post("/webhook/line")
async def line_webhook(request: Request):
    """LINE Webhook エンドポイント"""
    line_service, sheet_service, phone_service, settings = _get_services(request)
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
        line_id = event.get("source", {}).get("userId")
        if not line_id:
            continue

        # Postbackイベント処理
        if event_type == "postback":
            postback = event.get("postback", {})
            data_raw = postback.get("data", "{}")

            try:
                data = json.loads(data_raw)
            except json.JSONDecodeError:
                # URL形式のデータの場合
                data = _parse_postback_data(data_raw)

            action = data.get("action")

            # 出発報告
            if action == "departure_report":
                await _handle_departure_report(
                    event, line_id, line_service, sheet_service, phone_service, tz, logger
                )

            # 起床報告（enable_wakeup_watch有効時のみ）
            elif action == "wakeup_report" and settings.enable_wakeup_watch:
                await _handle_wakeup_report(
                    event, line_id, line_service, sheet_service, phone_service, tz, logger
                )

            # 起床予定時間ON（enable_wakeup_watch有効時のみ）
            elif action == "enable_wakeup_watch" and settings.enable_wakeup_watch:
                await _handle_wakeup_toggle(line_id, True, line_service, sheet_service, logger)

            # 起床予定時間OFF（enable_wakeup_watch有効時のみ）
            elif action == "disable_wakeup_watch" and settings.enable_wakeup_watch:
                await _handle_wakeup_toggle(line_id, False, line_service, sheet_service, logger)

        # メッセージイベント処理
        if event_type == "message":
            message = event.get("message", {})
            if message.get("type") != "text":
                continue

            text = message.get("text", "").strip()
            await _handle_text_message(
                text, line_id, line_service, sheet_service, tz, logger, settings
            )

    return {"status": "ok"}


def _parse_postback_data(data_raw: str) -> dict:
    """URL形式のPostbackデータをパース"""
    result = {}
    for pair in data_raw.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            result[key] = value
    return result


async def _handle_departure_report(
    event, line_id, line_service, sheet_service, phone_service, tz, logger
):
    """出発報告を処理"""
    event_ts = event.get("timestamp")
    actual_time = datetime.fromtimestamp(event_ts / 1000, tz=tz) if event_ts else datetime.now(tz)
    today = actual_time.date()

    found = sheet_service.get_departure_record(today, line_id)
    if found:
        _, record = found
        if record.actual_departure_time:
            await line_service.send_message(line_id, "既に出発報告済みです。")
            return
    else:
        cast = sheet_service.get_cast_by_line_id(line_id)
        if not cast:
            await line_service.send_message(line_id, "登録情報が見つかりません。")
            return
        record = DepartureRecord(
            date=today.isoformat(),
            name=cast.name,
            line_id=line_id,
        )

    if record.scheduled_departure_time is None:
        await line_service.send_message(line_id, "出発予定時間が未登録です。")
        return

    # 判定
    status = judge_departure(record.scheduled_departure_time, actual_time, tz)
    record.actual_departure_time = actual_time
    record.departure_status = status
    sheet_service.upsert_departure_record(record)

    # 電話をキャンセル
    phone_service.cancel_departure_calls(line_id)

    await line_service.send_message(line_id, "出発報告を受け付けました。")


async def _handle_wakeup_report(
    event, line_id, line_service, sheet_service, phone_service, tz, logger
):
    """起床報告を処理"""
    event_ts = event.get("timestamp")
    actual_time = datetime.fromtimestamp(event_ts / 1000, tz=tz) if event_ts else datetime.now(tz)
    today = actual_time.date()

    found = sheet_service.get_departure_record(today, line_id)
    if found:
        _, record = found
        if record.actual_wakeup_time:
            await line_service.send_message(line_id, "既に起床報告済みです。")
            return
    else:
        cast = sheet_service.get_cast_by_line_id(line_id)
        if not cast:
            await line_service.send_message(line_id, "登録情報が見つかりません。")
            return
        record = DepartureRecord(
            date=today.isoformat(),
            name=cast.name,
            line_id=line_id,
        )

    if record.scheduled_wakeup_time is None:
        await line_service.send_message(line_id, "起床予定時間が未登録です。")
        return

    # 判定
    status = judge_wakeup(record.scheduled_wakeup_time, actual_time, tz)
    record.actual_wakeup_time = actual_time
    record.wakeup_status = status
    sheet_service.upsert_departure_record(record)

    # 電話をキャンセル
    phone_service.cancel_wakeup_calls(line_id)

    await line_service.send_message(line_id, "起床報告を受け付けました。")


async def _handle_wakeup_toggle(line_id, enabled, line_service, sheet_service, logger):
    """起床予定時間のON/OFF切り替え"""
    success = sheet_service.update_cast_wakeup_setting(line_id, enabled)

    if success:
        if enabled:
            await line_service.send_message(
                line_id,
                "起床予定時間の登録機能をONにしました。"
            )
        else:
            await line_service.send_message(
                line_id,
                "起床予定時間の登録機能をOFFにしました。"
            )
    else:
        await line_service.send_message(line_id, "設定の更新に失敗しました。")


async def _handle_text_message(text, line_id, line_service, sheet_service, tz, logger, settings):
    """テキストメッセージを処理"""
    # 「出発 HH:MM」形式
    departure_match = re.match(r"^出発\s*(\d{1,2}:\d{2})$", text)
    if departure_match:
        time_str = departure_match.group(1)
        await _register_time(
            line_id, time_str, "departure", line_service, sheet_service, tz, logger, settings
        )
        return

    # 「起床 HH:MM」形式（enable_wakeup_watch有効時のみ）
    wakeup_match = re.match(r"^起床\s*(\d{1,2}:\d{2})$", text)
    if wakeup_match and settings.enable_wakeup_watch:
        time_str = wakeup_match.group(1)
        await _register_time(
            line_id, time_str, "wakeup", line_service, sheet_service, tz, logger, settings
        )
        return

    # 「HH:MM」形式（出発予定時間として登録）
    if validate_time_string(text):
        await _register_time(
            line_id, text, "departure", line_service, sheet_service, tz, logger, settings
        )
        return


async def _register_time(
    line_id, time_str, time_type, line_service, sheet_service, tz, logger, settings
):
    """時間を登録"""
    # 起床予定時間の場合、enable_wakeup_watch有効かチェック
    if time_type == "wakeup" and not settings.enable_wakeup_watch:
        return

    time_value = parse_time_string(time_str)
    if time_value is None:
        await line_service.send_message(
            line_id, "時間はHH:MM（5分単位）で入力してください。"
        )
        return

    cast = sheet_service.get_cast_by_line_id(line_id)
    if not cast:
        await line_service.send_message(line_id, "登録情報が見つかりません。")
        return

    # 起床予定時間の場合、キャストの機能がONか確認
    if time_type == "wakeup" and not cast.wakeup_time_registration_enabled:
        await line_service.send_message(
            line_id,
            "起床予定時間の登録機能がOFFになっています。"
            "ONにするには「起床予定時間ON」ボタンを押してください。"
        )
        return

    # 翌日の日付
    next_day = (datetime.now(tz) + timedelta(days=1)).date()

    # 既存のレコードを取得または新規作成
    found = sheet_service.get_departure_record(next_day, line_id)
    if found:
        _, record = found
    else:
        record = DepartureRecord(
            date=next_day.isoformat(),
            name=cast.name,
            line_id=line_id,
        )

    # 時間を設定
    if time_type == "departure":
        record.scheduled_departure_time = time_value
        sheet_service.upsert_departure_record(record)
        await line_service.send_message(
            line_id, f"出発予定時間を{time_str}で登録しました。"
        )
    else:
        record.scheduled_wakeup_time = time_value
        sheet_service.upsert_departure_record(record)
        await line_service.send_message(
            line_id, f"起床予定時間を{time_str}で登録しました。"
        )
