from datetime import date
from typing import List

from app.config import Settings
from app.services.line_service import LineService
from app.services.spreadsheet_service import SpreadsheetService
from app.utils.logger import get_logger


class NotificationService:
    def __init__(self, settings: Settings, line_service: LineService, sheet_service: SpreadsheetService) -> None:
        self._settings = settings
        self._line = line_service
        self._sheet = sheet_service
        self._logger = get_logger("notification_service")

    async def send_reminder_to_unregistered(self, target_date: date) -> int:
        unregistered = self._get_unregistered_casts(target_date)
        count = 0
        for cast in unregistered:
            ok = await self._line.send_message(cast["line_id"], "明日の出発予定時間を登録してください。")
            if ok:
                count += 1
        return count

    async def notify_control_unregistered(self, target_date: date) -> bool:
        if not self._settings.control_line_id:
            self._logger.warning("CONTROL_LINE_ID not set; skipping control notification")
            return False
        unregistered = self._get_unregistered_casts(target_date)
        if not unregistered:
            return True
        names = "\n".join([f"- {c['name']}" for c in unregistered])
        message = f"【事前通知】出発予定時間未登録者\n日付: {target_date.isoformat()}\n人数: {len(unregistered)}\n氏名:\n{names}"
        return await self._line.send_message(self._settings.control_line_id, message)

    async def send_emergency_alert(self, name: str, line_id: str, scheduled_time: str, now: str, phase1_done: bool, phase2_done: bool) -> bool:
        if not self._settings.control_line_id:
            self._logger.warning("CONTROL_LINE_ID not set; skipping emergency alert")
            return False
        message = (
            "【緊急アラート】出発報告なし\n"
            f"氏名: {name}\n"
            f"LINE_ID: {line_id}\n"
            f"出発予定時間: {scheduled_time}\n"
            f"現在時刻: {now}\n"
            f"電話①: {'完了' if phase1_done else '未完了'}\n"
            f"電話②: {'完了' if phase2_done else '未完了'}"
        )
        return await self._line.send_message(self._settings.control_line_id, message)

    async def notify_control_missing_default(self, target_date: date, names: List[str]) -> bool:
        if not self._settings.control_line_id:
            self._logger.warning("CONTROL_LINE_ID not set; skipping control notification")
            return False
        if not names:
            return True
        name_list = "\n".join([f"- {name}" for name in names])
        message = (
            "【事前通知】通常出発予定時間未登録\n"
            f"日付: {target_date.isoformat()}\n"
            f"人数: {len(names)}\n"
            f"氏名:\n{name_list}"
        )
        return await self._line.send_message(self._settings.control_line_id, message)

    def _get_unregistered_casts(self, target_date: date) -> List[dict]:
        casts = self._sheet.get_casts()
        records = self._sheet.get_departure_records(target_date)
        scheduled = {record.line_id for record in records if record.scheduled_departure_time}
        unregistered = [
            {"name": cast.name, "line_id": cast.line_id}
            for cast in casts
            if cast.line_id not in scheduled
        ]
        return unregistered
