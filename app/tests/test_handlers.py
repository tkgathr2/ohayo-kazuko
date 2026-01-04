from datetime import datetime, date, time
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI
from starlette.testclient import TestClient

from app.handlers.webhook_handler import router
from app.models import DepartureRecord


class FakeLineService:
    def __init__(self):
        self.messages = []

    def verify_signature(self, body: bytes, signature: str) -> bool:
        return True

    async def send_message(self, line_id: str, message: str) -> bool:
        self.messages.append((line_id, message))
        return True


class FakeSheetService:
    def __init__(self):
        self.records = {}
        self.casts = [{"name": "Test", "line_id": "U1", "phone_number": "+819012345678"}]

    def get_casts(self):
        return [type("Cast", (), c) for c in self.casts]

    def get_cast_by_line_id(self, line_id: str):
        for c in self.casts:
            if c["line_id"] == line_id:
                return type("Cast", (), c)
        return None

    def get_departure_record(self, target_date: date, line_id: str):
        # Convert date to string for lookup
        date_str = target_date.strftime("%Y-%m-%d") if isinstance(target_date, date) else target_date
        key = (date_str, line_id)
        if key in self.records:
            return 2, self.records[key]
        return None

    def upsert_departure_record(self, record: DepartureRecord):
        self.records[(record.date, record.line_id)] = record

    def get_departure_records(self, target_date: date):
        date_str = target_date.strftime("%Y-%m-%d") if isinstance(target_date, date) else target_date
        return [r for (d, _), r in self.records.items() if d == date_str]


class FakePhoneService:
    def __init__(self):
        self.canceled_departure = []
        self.canceled_wakeup = []

    def cancel_departure_calls(self, line_id: str) -> None:
        self.canceled_departure.append(line_id)

    def cancel_wakeup_calls(self, line_id: str) -> None:
        self.canceled_wakeup.append(line_id)


def build_app():
    app = FastAPI()
    app.include_router(router)
    app.state.line_service = FakeLineService()
    app.state.sheet_service = FakeSheetService()
    app.state.phone_service = FakePhoneService()
    return app


def test_register_time_message():
    app = build_app()
    client = TestClient(app)
    body = {
        "events": [
            {
                "type": "message",
                "message": {"type": "text", "text": "08:30"},
                "source": {"userId": "U1"},
            }
        ]
    }
    resp = client.post("/webhook/line", json=body, headers={"X-Line-Signature": "test"})
    assert resp.status_code == 200
    records = app.state.sheet_service.records
    assert records


def test_departure_report_postback():
    app = build_app()
    tz = ZoneInfo("Asia/Tokyo")
    now = datetime.now(tz)
    record = DepartureRecord(
        date=now.strftime("%Y-%m-%d"),
        name="Test",
        line_id="U1",
        scheduled_departure_time=time(now.hour, now.minute),
    )
    app.state.sheet_service.upsert_departure_record(record)

    client = TestClient(app)
    body = {
        "events": [
            {
                "type": "postback",
                "timestamp": int(datetime.now(tz).timestamp() * 1000),
                "postback": {"data": "{\"action\": \"departure_report\"}"},
                "source": {"userId": "U1"},
            }
        ]
    }
    resp = client.post("/webhook/line", json=body, headers={"X-Line-Signature": "test"})
    assert resp.status_code == 200
    updated = app.state.sheet_service.get_departure_record(record.date, "U1")[1]
    assert updated.actual_departure_time is not None
