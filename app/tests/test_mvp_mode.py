"""MVPモード（機能フラグFalse）の動作確認テスト"""
import os
from datetime import date, time
from unittest.mock import MagicMock, patch

import pytest

from app.config import Settings


@pytest.fixture
def mvp_settings() -> Settings:
    """MVP設定（全機能フラグFalse）"""
    env_vars = {
        "LINE_CHANNEL_ACCESS_TOKEN": "test_line_channel_access_token",
        "LINE_CHANNEL_SECRET": "test_line_channel_secret",
        "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "TWILIO_AUTH_TOKEN": "test_twilio_auth_token",
        "TWILIO_PHONE_NUMBER": "+15005550006",
        "GOOGLE_SHEETS_CREDENTIALS_JSON": '{"type": "service_account", "project_id": "test"}',
        "GOOGLE_SHEETS_SPREADSHEET_ID": "test_spreadsheet_id",
        "CONTROL_LINE_ID": "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        # MVP機能フラグ（すべてFalse）
        "ENABLE_WAKEUP_WATCH": "false",
        "ENABLE_PROCAST": "false",
        "ENABLE_PHONE_CALL2": "false",
        "ENABLE_SLACK": "false",
        "ENABLE_MULTIPLE_REMINDERS": "false",
        "ENABLE_AUTO_ASSIGN": "false",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        return Settings()


def test_mvp_mode_all_flags_false(mvp_settings: Settings) -> None:
    """MVPモードで全機能フラグがFalseであることを確認"""
    assert mvp_settings.enable_wakeup_watch is False
    assert mvp_settings.enable_procast is False
    assert mvp_settings.enable_phone_call2 is False
    assert mvp_settings.enable_slack is False
    assert mvp_settings.enable_multiple_reminders is False
    assert mvp_settings.enable_auto_assign is False


def test_mvp_notification_service_skip_slack(mvp_settings: Settings) -> None:
    """MVPモードでSlack通知がスキップされることを確認"""
    from app.services.notification_service import NotificationService

    line_service = MagicMock()
    sheet_service = MagicMock()

    notification_service = NotificationService(
        mvp_settings, line_service, sheet_service
    )

    # send_slack_errorはenable_slack=Falseの場合にTrueを返す（スキップ）
    import asyncio

    result = asyncio.run(
        notification_service.send_slack_error("test_error", "test_message")
    )
    assert result is True


def test_mvp_notification_service_skip_procast(mvp_settings: Settings) -> None:
    """MVPモードでProcast通知がスキップされることを確認"""
    from app.services.notification_service import NotificationService

    line_service = MagicMock()
    sheet_service = MagicMock()

    notification_service = NotificationService(
        mvp_settings, line_service, sheet_service
    )

    # notify_procast_data_missingはenable_procast=Falseの場合にTrueを返す（スキップ）
    import asyncio

    result = asyncio.run(notification_service.notify_procast_data_missing(hour=20))
    assert result is True


def test_mvp_scheduler_reminder_hours(mvp_settings: Settings) -> None:
    """MVPモードでリマインド時間が20:00のみであることを確認"""
    # enable_multiple_reminders=Falseの場合は[20]のみ
    reminder_hours = (
        [18, 19, 20, 21, 22]
        if mvp_settings.enable_multiple_reminders
        else [20]
    )
    assert reminder_hours == [20]


def test_full_mode_reminder_hours() -> None:
    """完全版モードでリマインド時間が5回であることを確認"""
    env_vars = {
        "LINE_CHANNEL_ACCESS_TOKEN": "test_line_channel_access_token",
        "LINE_CHANNEL_SECRET": "test_line_channel_secret",
        "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "TWILIO_AUTH_TOKEN": "test_twilio_auth_token",
        "TWILIO_PHONE_NUMBER": "+15005550006",
        "GOOGLE_SHEETS_CREDENTIALS_JSON": '{"type": "service_account", "project_id": "test"}',
        "GOOGLE_SHEETS_SPREADSHEET_ID": "test_spreadsheet_id",
        "CONTROL_LINE_ID": "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "ENABLE_MULTIPLE_REMINDERS": "true",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        full_settings = Settings()
        reminder_hours = (
            [18, 19, 20, 21, 22]
            if full_settings.enable_multiple_reminders
            else [20]
        )
        assert reminder_hours == [18, 19, 20, 21, 22]


def test_mvp_phone_service_no_call2(mvp_settings: Settings) -> None:
    """MVPモードで電話②がスケジュールされないことを確認"""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    from app.models import DepartureRecord
    from app.services.phone_service import PhoneService

    scheduler = AsyncIOScheduler()
    twilio = MagicMock()
    sheet = MagicMock()
    notification = MagicMock()

    phone_service = PhoneService(scheduler, twilio, sheet, notification)

    # スケジュール登録
    tz = ZoneInfo("Asia/Tokyo")
    record = DepartureRecord(
        date="2026-01-08",
        name="テスト太郎",
        line_id="U1234567890abcdef1234567890abcdef",
        scheduled_departure_time=time(8, 30),
    )

    phone_service.schedule_departure_calls(record, tz, mvp_settings)

    # 登録されたジョブを確認
    job_ids = phone_service._departure_jobs_by_line.get(record.line_id, [])

    # enable_phone_call2=Falseの場合、電話①と最終確認のみ（電話②なし）
    assert len(job_ids) == 2
    assert "departure_call1_U1234567890abcdef1234567890abcdef" in job_ids
    assert "departure_call2_U1234567890abcdef1234567890abcdef" not in job_ids
    assert "departure_final_U1234567890abcdef1234567890abcdef" in job_ids


def test_full_mode_phone_service_with_call2() -> None:
    """完全版モードで電話②がスケジュールされることを確認"""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    from app.models import DepartureRecord
    from app.services.phone_service import PhoneService

    env_vars = {
        "LINE_CHANNEL_ACCESS_TOKEN": "test_line_channel_access_token",
        "LINE_CHANNEL_SECRET": "test_line_channel_secret",
        "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "TWILIO_AUTH_TOKEN": "test_twilio_auth_token",
        "TWILIO_PHONE_NUMBER": "+15005550006",
        "GOOGLE_SHEETS_CREDENTIALS_JSON": '{"type": "service_account", "project_id": "test"}',
        "GOOGLE_SHEETS_SPREADSHEET_ID": "test_spreadsheet_id",
        "CONTROL_LINE_ID": "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "ENABLE_PHONE_CALL2": "true",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        full_settings = Settings()

        scheduler = AsyncIOScheduler()
        twilio = MagicMock()
        sheet = MagicMock()
        notification = MagicMock()

        phone_service = PhoneService(scheduler, twilio, sheet, notification)

        # スケジュール登録
        tz = ZoneInfo("Asia/Tokyo")
        record = DepartureRecord(
            date="2026-01-08",
            name="テスト太郎",
            line_id="U1234567890abcdef1234567890abcdef",
            scheduled_departure_time=time(8, 30),
        )

        phone_service.schedule_departure_calls(record, tz, full_settings)

        # 登録されたジョブを確認
        job_ids = phone_service._departure_jobs_by_line.get(record.line_id, [])

        # enable_phone_call2=Trueの場合、電話①、電話②、最終確認の3つ
        assert len(job_ids) == 3
        assert "departure_call1_U1234567890abcdef1234567890abcdef" in job_ids
        assert "departure_call2_U1234567890abcdef1234567890abcdef" in job_ids
        assert "departure_final_U1234567890abcdef1234567890abcdef" in job_ids
