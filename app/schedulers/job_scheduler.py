"""スケジューラー設定（起床リマインド、Procast通知対応）"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import Settings
from app.services.notification_service import NotificationService
from app.services.phone_service import PhoneService
from app.services.procast_service import ProcastService
from app.services.spreadsheet_service import SpreadsheetService
from app.utils.logger import get_logger


def start_scheduler(
    scheduler: AsyncIOScheduler,
    notification_service: NotificationService,
    phone_service: PhoneService,
    sheet_service: SpreadsheetService,
    procast_service: ProcastService,
    settings: Settings,
) -> None:
    """スケジューラーを開始"""
    logger = get_logger("job_scheduler")
    tz = ZoneInfo("Asia/Tokyo")

    # リマインドジョブ
    # enable_multiple_remindersがFalseの場合は20:00のみ、Trueの場合は18:00, 19:00, 20:00, 21:00, 22:00
    reminder_hours = [18, 19, 20, 21, 22] if settings.enable_multiple_reminders else [20]
    for hour in reminder_hours:
        # 出発予定時間リマインド
        scheduler.add_job(
            _remind_departure_unregistered,
            "cron",
            hour=hour,
            minute=0,
            timezone=tz,
            args=[notification_service, procast_service, tz],
            id=f"remind_departure_{hour}",
            replace_existing=True,
        )
        # 起床予定時間リマインド（enable_wakeup_watch有効時のみ）
        if settings.enable_wakeup_watch:
            scheduler.add_job(
                _remind_wakeup_unregistered,
                "cron",
                hour=hour,
                minute=0,
                timezone=tz,
                args=[notification_service, procast_service, tz],
                id=f"remind_wakeup_{hour}",
                replace_existing=True,
            )
        # Procastデータ未取得通知（enable_procast有効時のみ）
        if settings.enable_procast:
            scheduler.add_job(
                _notify_procast_missing,
                "cron",
                hour=hour,
                minute=0,
                timezone=tz,
                args=[notification_service, procast_service, hour],
                id=f"procast_missing_{hour}",
                replace_existing=True,
            )

    # 管制通知ジョブ（22:30）
    scheduler.add_job(
        _notify_control,
        "cron",
        hour=22,
        minute=30,
        timezone=tz,
        args=[notification_service, procast_service, tz],
        id="notify_control",
        replace_existing=True,
    )

    # 通常時間自動採用ジョブ（24:00 = 0:00）（enable_auto_assign有効時のみ）
    if settings.enable_auto_assign:
        scheduler.add_job(
            _auto_assign_and_schedule,
            "cron",
            hour=0,
            minute=0,
            timezone=tz,
            args=[notification_service, phone_service, sheet_service, tz, settings],
            id="auto_assign_default",
            replace_existing=True,
        )

    # Procastデータ取得ジョブ（18:00）（enable_procast有効時のみ）
    if settings.enable_procast:
        scheduler.add_job(
            _fetch_procast_data,
            "cron",
            hour=18,
            minute=0,
            timezone=tz,
            args=[procast_service],
            id="fetch_procast",
            replace_existing=True,
        )

    scheduler.start()
    logger.info("Scheduler started")

    # 起動時に既存の電話をスケジュール
    _schedule_existing_calls(phone_service, sheet_service, tz, settings)


def _tomorrow_date(tz: ZoneInfo):
    """翌日の日付を取得"""
    return (datetime.now(tz) + timedelta(days=1)).date()


async def _remind_departure_unregistered(
    notification_service: NotificationService,
    procast_service: ProcastService,
    tz: ZoneInfo,
) -> None:
    """出発予定時間未登録者にリマインド"""
    working_casts = None
    if procast_service.has_data():
        working_casts = procast_service.get_working_casts_tomorrow()

    await notification_service.send_reminder_to_unregistered(
        _tomorrow_date(tz),
        working_casts=working_casts,
        reminder_type="departure",
    )


async def _remind_wakeup_unregistered(
    notification_service: NotificationService,
    procast_service: ProcastService,
    tz: ZoneInfo,
) -> None:
    """起床予定時間未登録者にリマインド"""
    working_casts = None
    if procast_service.has_data():
        working_casts = procast_service.get_working_casts_tomorrow()

    await notification_service.send_reminder_to_unregistered(
        _tomorrow_date(tz),
        working_casts=working_casts,
        reminder_type="wakeup",
    )


async def _notify_procast_missing(
    notification_service: NotificationService,
    procast_service: ProcastService,
    hour: int,
) -> None:
    """Procastデータ未取得通知"""
    if procast_service.has_data():
        return
    await notification_service.notify_procast_data_missing(hour)


async def _notify_control(
    notification_service: NotificationService,
    procast_service: ProcastService,
    tz: ZoneInfo,
) -> None:
    """管制に未登録者を通知"""
    working_casts = None
    if procast_service.has_data():
        working_casts = procast_service.get_working_casts_tomorrow()

    await notification_service.notify_control_unregistered(
        _tomorrow_date(tz),
        working_casts=working_casts,
    )


async def _auto_assign_and_schedule(
    notification_service: NotificationService,
    phone_service: PhoneService,
    sheet_service: SpreadsheetService,
    tz: ZoneInfo,
    settings: Settings,
) -> None:
    """通常時間を自動採用し、電話をスケジュール"""
    target_date = datetime.now(tz).date()

    # 通常時間を自動採用
    missing_departure, missing_wakeup = sheet_service.auto_assign_default_times(target_date)

    # 未登録者を通知
    if missing_departure or missing_wakeup:
        await notification_service.notify_control_missing_default(
            target_date, missing_departure, missing_wakeup
        )

    # 電話をスケジュール
    _schedule_calls_for_date(phone_service, sheet_service, target_date, tz, settings)


async def _fetch_procast_data(procast_service: ProcastService) -> None:
    """Procastデータを取得"""
    await procast_service.fetch_procast_data()


def _schedule_existing_calls(
    phone_service: PhoneService,
    sheet_service: SpreadsheetService,
    tz: ZoneInfo,
    settings: Settings,
) -> None:
    """起動時に既存の電話をスケジュール"""
    today = datetime.now(tz).date()
    _schedule_calls_for_date(phone_service, sheet_service, today, tz, settings)


def _schedule_calls_for_date(
    phone_service: PhoneService,
    sheet_service: SpreadsheetService,
    target_date,
    tz: ZoneInfo,
    settings: Settings,
) -> None:
    """指定日の電話をスケジュール"""
    now = datetime.now(tz)
    records = sheet_service.get_departure_records(target_date)

    for record in records:
        # 出発電話のスケジュール
        if record.scheduled_departure_time and not record.actual_departure_time:
            scheduled_dt = datetime.combine(
                target_date, record.scheduled_departure_time, tzinfo=tz
            )
            # 予定時間+5分（電話①の時間）がまだ来ていない場合
            if scheduled_dt + timedelta(minutes=5) > now:
                phone_service.schedule_departure_calls(record, tz, settings)

        # 起床電話のスケジュール（enable_wakeup_watch有効時のみ）
        if settings.enable_wakeup_watch and record.scheduled_wakeup_time and not record.actual_wakeup_time:
            scheduled_dt = datetime.combine(
                target_date, record.scheduled_wakeup_time, tzinfo=tz
            )
            # 予定時間+5分（電話①の時間）がまだ来ていない場合
            if scheduled_dt + timedelta(minutes=5) > now:
                phone_service.schedule_wakeup_calls(record, tz, settings)
