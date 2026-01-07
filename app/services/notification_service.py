"""通知サービス（Slack通知対応）"""
from datetime import date, datetime
from typing import List, Optional, Set

import httpx
from zoneinfo import ZoneInfo

from app.config import Settings
from app.services.line_service import LineService
from app.services.spreadsheet_service import SpreadsheetService
from app.utils.error_handler import format_error_for_slack
from app.utils.logger import get_logger


class NotificationService:
    """通知サービス"""

    def __init__(
        self,
        settings: Settings,
        line_service: LineService,
        sheet_service: SpreadsheetService,
    ) -> None:
        self._settings = settings
        self._line = line_service
        self._sheet = sheet_service
        self._logger = get_logger("notification_service")
        self._tz = ZoneInfo(settings.tz)

    async def send_reminder_to_unregistered(
        self,
        target_date: date,
        working_casts: Optional[Set[str]] = None,
        reminder_type: str = "departure",
    ) -> int:
        """
        未登録者にリマインドを送信

        Args:
            target_date: 対象日
            working_casts: 翌日出勤のキャスト名セット（Procast連携時）
            reminder_type: "departure"（出発）または "wakeup"（起床）

        Returns:
            送信成功数
        """
        unregistered = self._get_unregistered_casts(
            target_date, working_casts, reminder_type
        )
        count = 0

        if reminder_type == "departure":
            message = "明日の出発予定時間を登録してください。"
        else:
            message = "明日の起床予定時間を登録してください。"

        for cast in unregistered:
            ok = await self._line.send_message(cast["line_id"], message)
            if ok:
                count += 1

        return count

    async def notify_control_unregistered(
        self,
        target_date: date,
        working_casts: Optional[Set[str]] = None,
    ) -> bool:
        """
        管制に未登録者を通知

        Args:
            target_date: 対象日
            working_casts: 翌日出勤のキャスト名セット

        Returns:
            送信成功時True
        """
        if not self._settings.control_line_id:
            self._logger.warning("CONTROL_LINE_ID not set; skipping control notification")
            return False

        # 出発予定時間未登録者
        departure_unregistered = self._get_unregistered_casts(
            target_date, working_casts, "departure"
        )
        # 起床予定時間未登録者
        wakeup_unregistered = self._get_unregistered_casts(
            target_date, working_casts, "wakeup"
        )

        messages = []

        if departure_unregistered:
            names = "\n".join([f"- {c['name']}" for c in departure_unregistered])
            messages.append(
                f"【事前通知】出発予定時間未登録者\n"
                f"日付: {target_date.isoformat()}\n"
                f"人数: {len(departure_unregistered)}\n"
                f"氏名:\n{names}"
            )

        if wakeup_unregistered:
            names = "\n".join([f"- {c['name']}" for c in wakeup_unregistered])
            messages.append(
                f"【事前通知】起床予定時間未登録者\n"
                f"日付: {target_date.isoformat()}\n"
                f"人数: {len(wakeup_unregistered)}\n"
                f"氏名:\n{names}"
            )

        if not messages:
            return True

        message = "\n\n".join(messages)

        # 複数の管制担当者に送信
        success = True
        for control_id in self._settings.control_line_ids:
            ok = await self._line.send_message(control_id, message)
            if not ok:
                success = False

        return success

    async def send_emergency_alert(
        self,
        name: str,
        line_id: str,
        scheduled_time: str,
        now: str,
        phase1_done: bool,
        phase2_done: bool,
        alert_type: str = "departure",
    ) -> bool:
        """
        管制に緊急アラートを送信

        Args:
            name: キャスト名
            line_id: LINE ID
            scheduled_time: 予定時間
            now: 現在時刻
            phase1_done: 電話①完了フラグ
            phase2_done: 電話②完了フラグ
            alert_type: "departure"（出発）または "wakeup"（起床）

        Returns:
            送信成功時True
        """
        if not self._settings.control_line_id:
            self._logger.warning("CONTROL_LINE_ID not set; skipping emergency alert")
            return False

        if alert_type == "departure":
            title = "【緊急アラート】出発報告なし"
            time_label = "出発予定時間"
        else:
            title = "【緊急アラート】起床報告なし"
            time_label = "起床予定時間"

        message = (
            f"{title}\n"
            f"氏名: {name}\n"
            f"LINE_ID: {line_id}\n"
            f"{time_label}: {scheduled_time}\n"
            f"現在時刻: {now}\n"
            f"電話①: {'完了' if phase1_done else '未完了'}\n"
            f"電話②: {'完了' if phase2_done else '未完了'}"
        )

        # 複数の管制担当者に送信
        success = True
        for control_id in self._settings.control_line_ids:
            ok = await self._line.send_message(control_id, message)
            if not ok:
                success = False

        return success

    async def notify_control_missing_default(
        self,
        target_date: date,
        departure_names: List[str],
        wakeup_names: Optional[List[str]] = None,
    ) -> bool:
        """
        管制に通常時間未登録者を通知

        Args:
            target_date: 対象日
            departure_names: 出発予定時間未登録者名リスト
            wakeup_names: 起床予定時間未登録者名リスト

        Returns:
            送信成功時True
        """
        if not self._settings.control_line_id:
            self._logger.warning("CONTROL_LINE_ID not set; skipping control notification")
            return False

        messages = []

        if departure_names:
            name_list = "\n".join([f"- {name}" for name in departure_names])
            messages.append(
                f"【事前通知】通常出発予定時間未登録\n"
                f"日付: {target_date.isoformat()}\n"
                f"人数: {len(departure_names)}\n"
                f"氏名:\n{name_list}"
            )

        if wakeup_names:
            name_list = "\n".join([f"- {name}" for name in wakeup_names])
            messages.append(
                f"【事前通知】通常起床予定時間未登録\n"
                f"日付: {target_date.isoformat()}\n"
                f"人数: {len(wakeup_names)}\n"
                f"氏名:\n{name_list}"
            )

        if not messages:
            return True

        message = "\n\n".join(messages)

        # 複数の管制担当者に送信
        success = True
        for control_id in self._settings.control_line_ids:
            ok = await self._line.send_message(control_id, message)
            if not ok:
                success = False

        return success

    async def notify_procast_data_missing(self, hour: int) -> bool:
        """
        Procastデータ未取得を通知

        Args:
            hour: 通知時刻（18, 19, 20, 21, 22）

        Returns:
            送信成功時True
        """
        message = "おはよう和子さんへのProcastデータが取得されていません。取り込みをお願いします"

        # 通知先を決定
        recipients = []

        if self._settings.control_line_id:
            recipients.extend(self._settings.control_line_ids)

        # 20:00以降は髙木にも通知
        if hour >= 20 and self._settings.takagi_line_id:
            recipients.append(self._settings.takagi_line_id)

        if not recipients:
            self._logger.warning("No recipients for Procast data missing notification")
            return False

        success = True
        for recipient in recipients:
            ok = await self._line.send_message(recipient, message)
            if not ok:
                success = False

        return success

    async def send_slack_error(
        self,
        error_type: str,
        error_message: str,
        additional_info: Optional[dict] = None,
    ) -> bool:
        """
        Slackにエラー通知を送信

        Args:
            error_type: エラータイプ
            error_message: エラーメッセージ
            additional_info: 追加情報

        Returns:
            送信成功時True
        """
        if not self._settings.slack_webhook_url:
            self._logger.warning("SLACK_WEBHOOK_URL not set; skipping Slack notification")
            return False

        try:
            payload = format_error_for_slack(error_type, error_message, additional_info)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._settings.slack_webhook_url,
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()
                return True

        except Exception as exc:
            self._logger.error("Failed to send Slack notification: %s", exc)
            return False

    def _get_unregistered_casts(
        self,
        target_date: date,
        working_casts: Optional[Set[str]] = None,
        reminder_type: str = "departure",
    ) -> List[dict]:
        """
        未登録のキャスト一覧を取得

        Args:
            target_date: 対象日
            working_casts: 翌日出勤のキャスト名セット（Procast連携時）
            reminder_type: "departure"（出発）または "wakeup"（起床）

        Returns:
            未登録キャストのリスト
        """
        casts = self._sheet.get_casts()
        records = self._sheet.get_departure_records(target_date)

        if reminder_type == "departure":
            # 出発予定時間が登録済みのLINE ID
            registered = {
                record.line_id for record in records if record.scheduled_departure_time
            }
        else:
            # 起床予定時間が登録済みのLINE ID
            registered = {
                record.line_id for record in records if record.scheduled_wakeup_time
            }

        unregistered = []
        for cast in casts:
            # 起床リマインドの場合、起床予定時間がONのキャストのみ対象
            if reminder_type == "wakeup" and not cast.wakeup_time_registration_enabled:
                continue

            # Procast連携時は翌日出勤のキャストのみ対象
            if working_casts is not None and cast.name not in working_casts:
                continue

            if cast.line_id not in registered:
                unregistered.append({"name": cast.name, "line_id": cast.line_id})

        return unregistered
