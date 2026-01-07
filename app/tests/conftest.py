"""テストフィクスチャ"""
import os
from datetime import date, datetime, time
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from app.config import Settings
from app.models import Cast, DepartureRecord, DepartureStatus, WakeupStatus


@pytest.fixture(autouse=True)
def mock_env_vars() -> Generator[None, None, None]:
    """環境変数をモック"""
    env_vars = {
        "LINE_CHANNEL_ACCESS_TOKEN": "test_line_channel_access_token",
        "LINE_CHANNEL_SECRET": "test_line_channel_secret",
        "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "TWILIO_AUTH_TOKEN": "test_twilio_auth_token",
        "TWILIO_PHONE_NUMBER": "+15005550006",
        "GOOGLE_SHEETS_CREDENTIALS_JSON": '{"type": "service_account", "project_id": "test"}',
        "GOOGLE_SHEETS_SPREADSHEET_ID": "test_spreadsheet_id",
        "CONTROL_LINE_ID": "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/test/test/test",
        "GOOGLE_DRIVE_CREDENTIALS_JSON": '{"type": "service_account", "project_id": "test"}',
        "GOOGLE_DRIVE_PROCAST_FOLDER_ID": "test_folder_id",
        "GOOGLE_DRIVE_PROCAST_FILE_NAME": "procast_data.csv",
        "TAKAGI_LINE_ID": "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "TZ": "Asia/Tokyo",
        "LOG_LEVEL": "DEBUG",
        "LOG_FILE": "./logs/test.log",
        # MVP機能フラグ（デフォルトでテスト用に全て有効化）
        "ENABLE_WAKEUP_WATCH": "true",
        "ENABLE_PROCAST": "true",
        "ENABLE_PHONE_CALL2": "true",
        "ENABLE_SLACK": "true",
        "ENABLE_MULTIPLE_REMINDERS": "true",
        "ENABLE_AUTO_ASSIGN": "true",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield


@pytest.fixture
def jst() -> ZoneInfo:
    """JST タイムゾーン"""
    return ZoneInfo("Asia/Tokyo")


@pytest.fixture
def sample_cast() -> Cast:
    """サンプルキャストデータ"""
    return Cast(
        name="テスト太郎",
        line_id="U1234567890abcdef1234567890abcdef",
        phone_number="+819012345678",
        default_departure_time=time(8, 30),
        wakeup_time_registration_enabled=True,
        default_wakeup_time=time(7, 0),
        wakeup_offset_minutes=0,
    )


@pytest.fixture
def sample_departure_record(jst: ZoneInfo) -> DepartureRecord:
    """サンプル出発記録データ"""
    today = datetime.now(jst).date()
    return DepartureRecord(
        date=today.isoformat(),
        name="テスト太郎",
        line_id="U1234567890abcdef1234567890abcdef",
        scheduled_departure_time=time(8, 30),
        actual_departure_time=None,
        departure_status=None,
        departure_phone_call_count=0,
        scheduled_wakeup_time=time(7, 0),
        actual_wakeup_time=None,
        wakeup_status=None,
        wakeup_phone_call_count=0,
        final_result=None,
    )


@pytest.fixture
def mock_line_service() -> MagicMock:
    """LINE サービスのモック"""
    mock = MagicMock()
    mock.send_message = AsyncMock(return_value=True)
    mock.verify_signature = MagicMock(return_value=True)
    mock.close = AsyncMock()
    return mock


@pytest.fixture
def mock_twilio_service() -> MagicMock:
    """Twilio サービスのモック"""
    mock = MagicMock()
    mock.make_call = AsyncMock(return_value="test_call_sid")
    mock.close = AsyncMock()
    return mock


@pytest.fixture
def mock_spreadsheet_service(sample_cast: Cast) -> MagicMock:
    """Spreadsheet サービスのモック"""
    mock = MagicMock()
    mock.get_casts = MagicMock(return_value=[sample_cast])
    mock.get_departure_records = MagicMock(return_value=[])
    mock.get_departure_record = MagicMock(return_value=None)
    mock.upsert_departure_record = MagicMock()
    mock.update_departure_actual_time = MagicMock()
    mock.update_departure_status = MagicMock()
    mock.auto_assign_default_times = MagicMock(return_value=[])
    mock.update_cast_wakeup_setting = MagicMock()
    return mock


@pytest.fixture
def mock_notification_service() -> MagicMock:
    """通知サービスのモック"""
    mock = MagicMock()
    mock.send_reminder_to_unregistered = AsyncMock(return_value=1)
    mock.notify_control_unregistered = AsyncMock(return_value=True)
    mock.send_emergency_alert = AsyncMock(return_value=True)
    mock.notify_control_missing_default = AsyncMock(return_value=True)
    mock.send_slack_error = AsyncMock(return_value=True)
    mock.notify_procast_data_missing = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_procast_service() -> MagicMock:
    """Procast サービスのモック"""
    mock = MagicMock()
    mock.fetch_procast_data = AsyncMock(return_value={"test": True})
    mock.is_cast_working_tomorrow = MagicMock(return_value=True)
    mock.has_data = MagicMock(return_value=True)
    return mock
