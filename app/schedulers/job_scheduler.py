from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.notification_service import NotificationService
from app.services.phone_service import PhoneService
from app.services.spreadsheet_service import SpreadsheetService
from app.utils.logger import get_logger


def start_scheduler(
    scheduler: AsyncIOScheduler,
    notification_service: NotificationService,
    phone_service: PhoneService,
    sheet_service: SpreadsheetService,
) -> None:
    logger = get_logger("job_scheduler")
    tz = ZoneInfo("Asia/Tokyo")

    scheduler.add_job(
        _remind_unregistered,
        "cron",
        hour=20,
        minute=0,
        timezone=tz,
        args=[notification_service, tz],
        id="remind_20",
        replace_existing=True,
    )
    scheduler.add_job(
        _remind_unregistered,
        "cron",
        hour=21,
        minute=0,
        timezone=tz,
        args=[notification_service, tz],
        id="remind_21",
        replace_existing=True,
    )
    scheduler.add_job(
        _remind_unregistered,
        "cron",
        hour=22,
        minute=0,
        timezone=tz,
        args=[notification_service, tz],
        id="remind_22",
        replace_existing=True,
    )
    scheduler.add_job(
        _notify_control,
        "cron",
        hour=22,
        minute=30,
        timezone=tz,
        args=[notification_service, tz],
        id="notify_control",
        replace_existing=True,
    )
    scheduler.add_job(
        _remind_unregistered,
        "cron",
        hour=23,
        minute=0,
        timezone=tz,
        args=[notification_service, tz],
        id="remind_23",
        replace_existing=True,
    )
    scheduler.add_job(
        _auto_assign_and_schedule,
        "cron",
        hour=0,
        minute=0,
        timezone=tz,
        args=[notification_service, phone_service, sheet_service, tz],
        id="auto_assign_default",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started")

    _schedule_existing_calls(phone_service, sheet_service, tz)


def _tomorrow_date(tz: ZoneInfo):
    return (datetime.now(tz) + timedelta(days=1)).date()

async def _remind_unregistered(notification_service: NotificationService, tz: ZoneInfo) -> None:
    await notification_service.send_reminder_to_unregistered(_tomorrow_date(tz))


async def _notify_control(notification_service: NotificationService, tz: ZoneInfo) -> None:
    await notification_service.notify_control_unregistered(_tomorrow_date(tz))


async def _auto_assign_and_schedule(
    notification_service: NotificationService,
    phone_service: PhoneService,
    sheet_service: SpreadsheetService,
    tz: ZoneInfo,
) -> None:
    target_date = datetime.now(tz).date()
    missing = sheet_service.auto_assign_default_times(target_date)
    if missing:
        await notification_service.notify_control_missing_default(target_date, missing)
    _schedule_calls_for_date(phone_service, sheet_service, target_date, tz)


def _schedule_existing_calls(phone_service: PhoneService, sheet_service: SpreadsheetService, tz: ZoneInfo) -> None:
    today = datetime.now(tz).date()
    _schedule_calls_for_date(phone_service, sheet_service, today, tz)


def _schedule_calls_for_date(
    phone_service: PhoneService,
    sheet_service: SpreadsheetService,
    target_date,
    tz: ZoneInfo,
) -> None:
    now = datetime.now(tz)
    records = sheet_service.get_departure_records(target_date)
    for record in records:
        if not record.scheduled_departure_time or record.actual_departure_time:
            continue
        if record.scheduled_departure_time + timedelta(minutes=1) < now:
            continue
        phone_service.schedule_calls_for_record(record)

