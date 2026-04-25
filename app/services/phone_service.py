"""電話サービス（起床電話対応）"""
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo

from app.config import Settings
from app.models import DepartureRecord, DepartureStatus, FinalResult, WakeupStatus
from app.services.notification_service import NotificationService
from app.services.spreadsheet_service import SpreadsheetService
from app.services.twilio_service import TwilioService
from app.utils.logger import get_logger


# 電話メッセージ
DEPARTURE_CALL_MESSAGE = "おはよう和子さんです。出発報告をお願いします。"
WAKEUP_CALL_MESSAGE = "おはよう和子さんです。起床報告をお願いします。"


class PhoneService:
    """電話サービス"""

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
        self._logger = get_logger("phone_service")
        # 出発電話のジョブID
        self._departure_jobs_by_line: Dict[str, List[str]] = {}
        # 起床電話のジョブID
        self._wakeup_jobs_by_line: Dict[str, List[str]] = {}
        # 発信済みコールSID（進行中の電話をキャンセルするために保存）
        self._departure_call_sids_by_line: Dict[str, List[str]] = {}
        self._wakeup_call_sids_by_line: Dict[str, List[str]] = {}

    def schedule_departure_calls(self, record: DepartureRecord, tz: ZoneInfo, settings: Settings) -> None:
        """
        出発電話をスケジュール

        - 電話①: 出発予定時間から5分経過後
        - 電話②: 電話①から10分経過後（enable_phone_call2有効時のみ）
        """
        if not record.scheduled_departure_time:
            return

        target_date = date.fromisoformat(record.date)
        scheduled_dt = datetime.combine(target_date, record.scheduled_departure_time, tzinfo=tz)

        # 電話①: 5分後
        call1_time = scheduled_dt + timedelta(minutes=5)
        # 電話②: 電話①から10分後（=予定時間から15分後）
        call2_time = scheduled_dt + timedelta(minutes=15)

        date_str = target_date.isoformat()
        job_ids = []

        # 電話①
        job_id1 = f"departure_call1_{date_str}_{record.line_id}"
        self._scheduler.add_job(
            self._make_departure_call,
            "date",
            run_date=call1_time,
            args=[target_date, record.line_id, 1, tz],
            id=job_id1,
            replace_existing=True,
        )
        job_ids.append(job_id1)

        # 電話②（enable_phone_call2有効時のみ）
        if settings.enable_phone_call2:
            job_id2 = f"departure_call2_{date_str}_{record.line_id}"
            self._scheduler.add_job(
                self._make_departure_call,
                "date",
                run_date=call2_time,
                args=[target_date, record.line_id, 2, tz],
                id=job_id2,
                replace_existing=True,
            )
            job_ids.append(job_id2)

            # 最終確認（電話②から5分後）
            # （電話接続+TTS再生+LINE操作に要する時間を考慮して30秒→5分に延長）
            final_job_id = f"departure_final_{date_str}_{record.line_id}"
            self._scheduler.add_job(
                self._departure_final_check,
                "date",
                run_date=call2_time + timedelta(minutes=5),
                args=[target_date, record.line_id, tz],
                id=final_job_id,
                replace_existing=True,
            )
            job_ids.append(final_job_id)
        else:
            # 電話②が無効の場合、電話①から5分後に最終確認
            # （電話接続+TTS再生+LINE操作に要する時間を考慮して30秒→5分に延長）
            final_job_id = f"departure_final_{date_str}_{record.line_id}"
            self._scheduler.add_job(
                self._departure_final_check,
                "date",
                run_date=call1_time + timedelta(minutes=5),
                args=[target_date, record.line_id, tz],
                id=final_job_id,
                replace_existing=True,
            )
            job_ids.append(final_job_id)

        self._departure_jobs_by_line[record.line_id] = job_ids

    def schedule_wakeup_calls(self, record: DepartureRecord, tz: ZoneInfo, settings: Settings) -> None:
        """
        起床電話をスケジュール

        - 電話①: 起床予定時間から5分経過後
        - 電話②: 電話①から10分経過後（enable_phone_call2有効時のみ）
        """
        if not record.scheduled_wakeup_time:
            return

        target_date = date.fromisoformat(record.date)
        scheduled_dt = datetime.combine(target_date, record.scheduled_wakeup_time, tzinfo=tz)

        # 電話①: 5分後
        call1_time = scheduled_dt + timedelta(minutes=5)
        # 電話②: 電話①から10分後（=予定時間から15分後）
        call2_time = scheduled_dt + timedelta(minutes=15)

        date_str = target_date.isoformat()
        job_ids = []

        # 電話①
        job_id1 = f"wakeup_call1_{date_str}_{record.line_id}"
        self._scheduler.add_job(
            self._make_wakeup_call,
            "date",
            run_date=call1_time,
            args=[target_date, record.line_id, 1, tz],
            id=job_id1,
            replace_existing=True,
        )
        job_ids.append(job_id1)

        # 電話②（enable_phone_call2有効時のみ）
        if settings.enable_phone_call2:
            job_id2 = f"wakeup_call2_{date_str}_{record.line_id}"
            self._scheduler.add_job(
                self._make_wakeup_call,
                "date",
                run_date=call2_time,
                args=[target_date, record.line_id, 2, tz],
                id=job_id2,
                replace_existing=True,
            )
            job_ids.append(job_id2)

            # 最終確認（電話②から5分後）
            # （電話接続+TTS再生+LINE操作に要する時間を考慮して30秒→5分に延長）
            final_job_id = f"wakeup_final_{date_str}_{record.line_id}"
            self._scheduler.add_job(
                self._wakeup_final_check,
                "date",
                run_date=call2_time + timedelta(minutes=5),
                args=[target_date, record.line_id, tz],
                id=final_job_id,
                replace_existing=True,
            )
            job_ids.append(final_job_id)
        else:
            # 電話②が無効の場合、電話①から5分後に最終確認
            # （電話接続+TTS再生+LINE操作に要する時間を考慮して30秒→5分に延長）
            final_job_id = f"wakeup_final_{date_str}_{record.line_id}"
            self._scheduler.add_job(
                self._wakeup_final_check,
                "date",
                run_date=call1_time + timedelta(minutes=5),
                args=[target_date, record.line_id, tz],
                id=final_job_id,
                replace_existing=True,
            )
            job_ids.append(final_job_id)

        self._wakeup_jobs_by_line[record.line_id] = job_ids

    def cancel_departure_calls(self, line_id: str) -> None:
        """出発電話をキャンセル（スケジューラーから削除＋進行中のTwilio電話もキャンセル）"""
        # APSchedulerジョブをキャンセル
        for job_id in self._departure_jobs_by_line.get(line_id, []):
            try:
                self._scheduler.remove_job(job_id)
            except Exception:
                pass
        self._departure_jobs_by_line.pop(line_id, None)

        # 進行中のTwilio電話をキャンセル（fire-and-forget）
        for sid in self._departure_call_sids_by_line.pop(line_id, []):
            self._schedule_twilio_cancel(sid)

    def cancel_wakeup_calls(self, line_id: str) -> None:
        """起床電話をキャンセル（スケジューラーから削除＋進行中のTwilio電話もキャンセル）"""
        # APSchedulerジョブをキャンセル
        for job_id in self._wakeup_jobs_by_line.get(line_id, []):
            try:
                self._scheduler.remove_job(job_id)
            except Exception:
                pass
        self._wakeup_jobs_by_line.pop(line_id, None)

        # 進行中のTwilio電話をキャンセル（fire-and-forget）
        for sid in self._wakeup_call_sids_by_line.pop(line_id, []):
            self._schedule_twilio_cancel(sid)

    def _schedule_twilio_cancel(self, call_sid: str) -> None:
        """イベントループが実行中の場合にTwilioキャンセルをスケジュール"""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._cancel_twilio_call(call_sid))
        except RuntimeError:
            # イベントループが取得できない場合（起動時スケジュールなど）はスキップ
            self._logger.warning("No running event loop for Twilio cancel, sid=%s", call_sid)

    async def _cancel_twilio_call(self, call_sid: str) -> None:
        """Twilio APIを使って進行中の電話をキャンセル"""
        try:
            ok = await self._twilio.cancel_call(call_sid)
            if not ok:
                self._logger.warning("Twilio cancel_call failed for sid=%s", call_sid)
        except Exception as exc:
            self._logger.error("Error cancelling Twilio call sid=%s: %s", call_sid, exc)

    async def _make_departure_call(
        self, record_date: date, line_id: str, call_number: int, tz: ZoneInfo
    ) -> None:
        """出発電話を発信"""
        found = self._sheet.get_departure_record(record_date, line_id)
        if not found:
            return
        _, record = found

        # 既に報告済みの場合はキャンセル
        if record.actual_departure_time:
            self.cancel_departure_calls(line_id)
            return

        # 電話回数を更新
        if call_number == 1 and record.departure_phone_call_count < 1:
            record.departure_phone_call_count = 1
            if record.departure_status != DepartureStatus.NEED_CHECK:
                record.departure_status = DepartureStatus.NEED_CHECK
            self._sheet.upsert_departure_record(record)
        elif call_number == 2 and record.departure_phone_call_count < 2:
            record.departure_phone_call_count = 2
            self._sheet.upsert_departure_record(record)

        # 電話番号を取得
        phone_number = self._get_phone_number(line_id)
        if not phone_number:
            self._logger.warning("Phone number missing for line_id=%s", line_id)
            return

        # 電話発信
        call_sid = await self._twilio.make_call(phone_number, DEPARTURE_CALL_MESSAGE)
        if not call_sid:
            self._logger.error("Failed to make departure call for line_id=%s", line_id)
        else:
            # 進行中の電話をキャンセルできるようSIDを保存
            if line_id not in self._departure_call_sids_by_line:
                self._departure_call_sids_by_line[line_id] = []
            self._departure_call_sids_by_line[line_id].append(call_sid)

    async def _make_wakeup_call(
        self, record_date: date, line_id: str, call_number: int, tz: ZoneInfo
    ) -> None:
        """起床電話を発信"""
        found = self._sheet.get_departure_record(record_date, line_id)
        if not found:
            return
        _, record = found

        # 既に報告済みの場合はキャンセル
        if record.actual_wakeup_time:
            self.cancel_wakeup_calls(line_id)
            return

        # 電話回数を更新
        if call_number == 1 and record.wakeup_phone_call_count < 1:
            record.wakeup_phone_call_count = 1
            if record.wakeup_status != WakeupStatus.NEED_CHECK:
                record.wakeup_status = WakeupStatus.NEED_CHECK
            self._sheet.upsert_departure_record(record)
        elif call_number == 2 and record.wakeup_phone_call_count < 2:
            record.wakeup_phone_call_count = 2
            self._sheet.upsert_departure_record(record)

        # 電話番号を取得
        phone_number = self._get_phone_number(line_id)
        if not phone_number:
            self._logger.warning("Phone number missing for line_id=%s", line_id)
            return

        # 電話発信
        call_sid = await self._twilio.make_call(phone_number, WAKEUP_CALL_MESSAGE)
        if not call_sid:
            self._logger.error("Failed to make wakeup call for line_id=%s", line_id)
        else:
            # 進行中の電話をキャンセルできるようSIDを保存
            if line_id not in self._wakeup_call_sids_by_line:
                self._wakeup_call_sids_by_line[line_id] = []
            self._wakeup_call_sids_by_line[line_id].append(call_sid)

    async def _departure_final_check(
        self, record_date: date, line_id: str, tz: ZoneInfo
    ) -> None:
        """出発の最終確認"""
        found = self._sheet.get_departure_record(record_date, line_id)
        if not found:
            return
        _, record = found

        # 既に報告済みの場合はキャンセル
        if record.actual_departure_time:
            self.cancel_departure_calls(line_id)
            return

        # 最終結果を「要管制」に設定
        record.final_result = FinalResult.NEED_CONTROL
        self._sheet.upsert_departure_record(record)

        # 管制に緊急アラート
        now = datetime.now(tz)
        scheduled_time = record.scheduled_departure_time.strftime("%H:%M") if record.scheduled_departure_time else ""
        await self._notification.send_emergency_alert(
            name=record.name,
            line_id=record.line_id,
            scheduled_time=scheduled_time,
            now=now.strftime("%Y-%m-%d %H:%M"),
            phase1_done=record.departure_phone_call_count >= 1,
            phase2_done=record.departure_phone_call_count >= 2,
            alert_type="departure",
        )

    async def _wakeup_final_check(
        self, record_date: date, line_id: str, tz: ZoneInfo
    ) -> None:
        """起床の最終確認"""
        found = self._sheet.get_departure_record(record_date, line_id)
        if not found:
            return
        _, record = found

        # 既に報告済みの場合はキャンセル
        if record.actual_wakeup_time:
            self.cancel_wakeup_calls(line_id)
            return

        # 最終結果を「要管制」に設定
        record.final_result = FinalResult.NEED_CONTROL
        self._sheet.upsert_departure_record(record)

        # 管制に緊急アラート
        now = datetime.now(tz)
        scheduled_time = record.scheduled_wakeup_time.strftime("%H:%M") if record.scheduled_wakeup_time else ""
        await self._notification.send_emergency_alert(
            name=record.name,
            line_id=record.line_id,
            scheduled_time=scheduled_time,
            now=now.strftime("%Y-%m-%d %H:%M"),
            phase1_done=record.wakeup_phone_call_count >= 1,
            phase2_done=record.wakeup_phone_call_count >= 2,
            alert_type="wakeup",
        )

    def _get_phone_number(self, line_id: str) -> Optional[str]:
        """LINE IDから電話番号を取得"""
        for cast in self._sheet.get_casts():
            if cast.line_id == line_id:
                return cast.phone_number
        return None
