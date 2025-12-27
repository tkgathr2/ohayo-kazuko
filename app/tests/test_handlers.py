from datetime import datetime, date
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from fastapi.testclient import TestClient

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

    def get_departure_record(self, target_date: date, line_id: str):
        key = (target_date, line_id)
        if key in self.records:
            return 2, self.records[key]
        return None

    def upsert_departure_record(self, record: DepartureRecord):
        self.records[(record.date, record.line_id)] = record

    def get_departure_records(self, target_date: date):
        return [r for (d, _), r in self.records.items() if d == target_date]


class FakePhoneService:
    def __init__(self):
        self.canceled = []

    def cancel_phone_calls(self, line_id: str) -> None:
        self.canceled.append(line_id)


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
    record = DepartureRecord(
        date=datetime.now(tz).date(),
        name="Test",
        line_id="U1",
        scheduled_departure_time=datetime.now(tz),
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
