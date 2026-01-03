from datetime import datetime, timedelta
from typing import Dict, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler

<<<<<<< HEAD
from app.models import DepartureRecord, DepartureStatus
from app.services.notification_service import NotificationService
=======
from app.models import DepartureRecord
>>>>>>> 394f6e5b5be191414b6d75579e5e0b9097ea38c9
from app.services.spreadsheet_service import SpreadsheetService
from app.services.twilio_service import TwilioService
from app.utils.logger import get_logger


CALL_MESSAGE = (
    "おはようございます。出発見守り和子さんです。"
    "本日の出発報告をお願いします。LINEの出発報告ボタンを押してください。"
)


class PhoneService:
<<<<<<< HEAD
    def __init__(
        self,
        scheduler: AsyncIOScheduler,
        twilio: TwilioService,
        sheet: SpreadsheetService,
        notification: NotificationService,
    ) -> None:
        self._scheduler = scheduler
        self._twilio = twilio
        self._sheet = sheet
        self._notification = notification
=======
    def __init__(self, scheduler: AsyncIOScheduler, twilio: TwilioService, sheet: SpreadsheetService) -> None:
        self._scheduler = scheduler
        self._twilio = twilio
        self._sheet = sheet
>>>>>>> 394f6e5b5be191414b6d75579e5e0b9097ea38c9
        self._logger = get_logger("phone_service")
        self._jobs_by_line: Dict[str, List[str]] = {}

    def schedule_calls_for_record(self, record: DepartureRecord) -> None:
        if not record.scheduled_departure_time:
            return
        start = record.scheduled_departure_time + timedelta(minutes=1)
        times = [start + timedelta(minutes=5 * i) for i in range(5)]
        times += [times[-1] + timedelta(minutes=3 * i) for i in range(1, 11)]

        job_ids = []
        for idx, call_time in enumerate(times):
            job_id = f"call_{record.line_id}_{idx}"
            self._scheduler.add_job(
                self._make_call_job,
                "date",
                run_date=call_time,
                args=[record.date, record.line_id, idx],
                id=job_id,
                replace_existing=True,
            )
            job_ids.append(job_id)

        final_job_id = f"final_check_{record.line_id}"
        self._scheduler.add_job(
            self._final_check_job,
            "date",
            run_date=times[-1] + timedelta(seconds=30),
            args=[record.date, record.line_id],
            id=final_job_id,
            replace_existing=True,
        )
        job_ids.append(final_job_id)
        self._jobs_by_line[record.line_id] = job_ids

    def cancel_phone_calls(self, line_id: str) -> None:
        for job_id in self._jobs_by_line.get(line_id, []):
            try:
                self._scheduler.remove_job(job_id)
            except Exception:
                pass
        self._jobs_by_line.pop(line_id, None)

    async def _make_call_job(self, record_date, line_id: str, index: int) -> None:
        found = self._sheet.get_departure_record(record_date, line_id)
        if not found:
            return
        _, record = found
        if record.actual_departure_time:
            self.cancel_phone_calls(line_id)
            return
        if index == 0 and record.phone_call_count < 1:
            record.phone_call_count = 1
            if record.departure_status != DepartureStatus.NEED_CHECK:
                record.departure_status = DepartureStatus.NEED_CHECK
            self._sheet.upsert_departure_record(record)
        if index == 5 and record.phone_call_count < 2:
            record.phone_call_count = 2
            self._sheet.upsert_departure_record(record)
        phone_number = None
        for cast in self._sheet.get_casts():
            if cast.line_id == line_id:
                phone_number = cast.phone_number
                break
        if not phone_number:
            self._logger.warning("Phone number missing for line_id=%s", line_id)
            return
        call_sid = await self._twilio.make_call(phone_number, CALL_MESSAGE)
        if not call_sid:
            record.control_notes = "電話発信失敗"
            self._sheet.upsert_departure_record(record)

    async def _final_check_job(self, record_date, line_id: str) -> None:
        found = self._sheet.get_departure_record(record_date, line_id)
        if not found:
            return
        _, record = found
        if record.actual_departure_time:
            self.cancel_phone_calls(line_id)
            return
        record.departure_status = DepartureStatus.CONTROL
        self._sheet.upsert_departure_record(record)

        now = datetime.now(record.scheduled_departure_time.tzinfo) if record.scheduled_departure_time else datetime.now()
        scheduled_time = record.scheduled_departure_time.strftime("%H:%M") if record.scheduled_departure_time else ""
        await self._notification.send_emergency_alert(
            name=record.name,
            line_id=record.line_id,
            scheduled_time=scheduled_time,
            now=now.strftime("%Y-%m-%d %H:%M"),
            phase1_done=True,
            phase2_done=True,
        )
