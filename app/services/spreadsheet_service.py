"""Google Sheets連携サービス"""
import json
from datetime import date, datetime, time
from typing import List, Optional, Tuple

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from zoneinfo import ZoneInfo

from app.config import Settings
from app.models import Cast, DepartureRecord, DepartureStatus, FinalResult, WakeupStatus
from app.utils.logger import get_logger


CAST_SHEET = "キャスト一覧"
DEPARTURE_SHEET = "出発予定時間_当日管理"


class SpreadsheetService:
    """Google Sheets サービス"""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = get_logger("spreadsheet_service")
        self._tz = ZoneInfo(settings.tz)
        self._service = None  # lazy init: initialized on first use

    def _get_service(self):
        """Google Sheets APIサービスを遅延初期化して返す"""
        if self._service is None:
            try:
                creds_info = json.loads(self._settings.google_sheets_credentials_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"GOOGLE_SHEETS_CREDENTIALS_JSON のJSONパースに失敗しました: {e}") from e
            creds = Credentials.from_service_account_info(
                creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            self._service = build("sheets", "v4", credentials=creds, cache_discovery=False)
        return self._service

    def _get_values(self, sheet_name: str) -> List[List[str]]:
        """シートの値を取得"""
        result = (
            self._get_service().spreadsheets()
            .values()
            .get(spreadsheetId=self._settings.google_sheets_spreadsheet_id, range=sheet_name)
            .execute()
        )
        return result.get("values", [])

    def _update_values(self, range_name: str, values: List[List[str]]) -> None:
        """シートの値を更新"""
        body = {"values": values}
        (
            self._get_service().spreadsheets()
            .values()
            .update(
                spreadsheetId=self._settings.google_sheets_spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )

    def _append_values(self, range_name: str, values: List[List[str]]) -> None:
        """シートに値を追加"""
        body = {"values": values}
        (
            self._get_service().spreadsheets()
            .values()
            .append(
                spreadsheetId=self._settings.google_sheets_spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )

    def get_casts(self) -> List[Cast]:
        """キャスト一覧を取得"""
        rows = self._get_values(CAST_SHEET)
        if not rows:
            return []
        header = rows[0]
        casts: List[Cast] = []
        for row in rows[1:]:
            data = dict(zip(header, row + [""] * (len(header) - len(row))))
            try:
                # 通常出発予定時間
                default_departure = None
                if data.get("通常出発予定時間"):
                    parts = data["通常出発予定時間"].split(":")
                    if len(parts) >= 2:
                        default_departure = time(int(parts[0]), int(parts[1]))

                # 起床予定時間登録ON/OFF
                wakeup_enabled = data.get("起床予定時間登録ON/OFF", "").upper() == "TRUE"

                # 通常起床予定時間
                default_wakeup = None
                if data.get("通常起床予定時間"):
                    parts = data["通常起床予定時間"].split(":")
                    if len(parts) >= 2:
                        default_wakeup = time(int(parts[0]), int(parts[1]))

                # 起床オフセット
                wakeup_offset = int(data.get("起床オフセット（分）", 0) or 0)

                cast = Cast(
                    name=data.get("氏名", ""),
                    line_id=data.get("LINE_ID", ""),
                    phone_number=data.get("電話番号", ""),
                    default_departure_time=default_departure,
                    wakeup_time_registration_enabled=wakeup_enabled,
                    default_wakeup_time=default_wakeup,
                    wakeup_offset_minutes=wakeup_offset,
                )
                casts.append(cast)
            except Exception as exc:
                self._logger.warning("Invalid cast row skipped: %s", exc)
        return casts

    def get_cast_by_line_id(self, line_id: str) -> Optional[Cast]:
        """LINE IDでキャストを取得"""
        for cast in self.get_casts():
            if cast.line_id == line_id:
                return cast
        return None

    def update_cast_wakeup_setting(self, line_id: str, enabled: bool) -> bool:
        """キャストの起床設定を更新"""
        rows = self._get_values(CAST_SHEET)
        if not rows:
            return False
        header = rows[0]

        # 起床予定時間登録ON/OFF列のインデックスを取得
        try:
            wakeup_col_idx = header.index("起床予定時間登録ON/OFF")
        except ValueError:
            self._logger.warning("起床予定時間登録ON/OFF column not found")
            return False

        for idx, row in enumerate(rows[1:], start=2):
            data = dict(zip(header, row + [""] * (len(header) - len(row))))
            if data.get("LINE_ID") == line_id:
                # 列番号をアルファベットに変換
                col_letter = chr(ord("A") + wakeup_col_idx)
                range_name = f"{CAST_SHEET}!{col_letter}{idx}"
                self._update_values(range_name, [["TRUE" if enabled else "FALSE"]])
                return True
        return False

    def get_departure_records(self, target_date: date) -> List[DepartureRecord]:
        """指定日の出発記録を取得"""
        rows = self._get_values(DEPARTURE_SHEET)
        if not rows:
            return []
        header = rows[0]
        records: List[DepartureRecord] = []
        for row in rows[1:]:
            data = dict(zip(header, row + [""] * (len(header) - len(row))))
            if data.get("日付") != target_date.isoformat():
                continue
            record = self._row_to_record(data)
            if record:
                records.append(record)
        return records

    def get_departure_record(
        self, target_date: date, line_id: str
    ) -> Optional[Tuple[int, DepartureRecord]]:
        """指定日・LINE IDの出発記録を取得"""
        rows = self._get_values(DEPARTURE_SHEET)
        if not rows:
            return None
        header = rows[0]
        for index, row in enumerate(rows[1:], start=2):
            data = dict(zip(header, row + [""] * (len(header) - len(row))))
            if data.get("日付") == target_date.isoformat() and data.get("LINE_ID") == line_id:
                record = self._row_to_record(data)
                if record:
                    return index, record
        return None

    def upsert_departure_record(self, record: DepartureRecord) -> None:
        """出発記録を更新または追加"""
        target_date = date.fromisoformat(record.date)
        found = self.get_departure_record(target_date, record.line_id)
        if found:
            row_index, _ = found
            range_name = f"{DEPARTURE_SHEET}!A{row_index}:L{row_index}"
            self._update_values(range_name, [self._record_to_row(record)])
            return
        self._append_values(f"{DEPARTURE_SHEET}!A:L", [self._record_to_row(record)])

    def update_departure_actual_time(
        self, target_date: date, line_id: str, actual_time: datetime
    ) -> None:
        """出発報告時刻を更新"""
        found = self.get_departure_record(target_date, line_id)
        if not found:
            return
        _, record = found
        record.actual_departure_time = actual_time
        self.upsert_departure_record(record)

    def update_wakeup_actual_time(
        self, target_date: date, line_id: str, actual_time: datetime
    ) -> None:
        """起床報告時刻を更新"""
        found = self.get_departure_record(target_date, line_id)
        if not found:
            return
        _, record = found
        record.actual_wakeup_time = actual_time
        self.upsert_departure_record(record)

    def update_departure_status(
        self, target_date: date, line_id: str, status: DepartureStatus
    ) -> None:
        """出発判定を更新"""
        found = self.get_departure_record(target_date, line_id)
        if not found:
            return
        _, record = found
        record.departure_status = status
        self.upsert_departure_record(record)

    def update_wakeup_status(
        self, target_date: date, line_id: str, status: WakeupStatus
    ) -> None:
        """起床判定を更新"""
        found = self.get_departure_record(target_date, line_id)
        if not found:
            return
        _, record = found
        record.wakeup_status = status
        self.upsert_departure_record(record)

    def auto_assign_default_times(self, target_date: date) -> Tuple[List[str], List[str]]:
        """
        通常時間を自動採用

        Returns:
            Tuple[出発予定時間未登録者名リスト, 起床予定時間未登録者名リスト]
        """
        casts = {cast.line_id: cast for cast in self.get_casts()}
        missing_departure = []
        missing_wakeup = []

        for line_id, cast in casts.items():
            found = self.get_departure_record(target_date, line_id)

            if not found:
                # レコードが存在しない場合、新規作成
                scheduled_departure = None
                scheduled_wakeup = None

                if cast.default_departure_time:
                    scheduled_departure = cast.default_departure_time
                else:
                    missing_departure.append(cast.name)

                if cast.wakeup_time_registration_enabled:
                    if cast.default_wakeup_time:
                        scheduled_wakeup = cast.default_wakeup_time
                    else:
                        missing_wakeup.append(cast.name)

                record = DepartureRecord(
                    date=target_date.isoformat(),
                    name=cast.name,
                    line_id=cast.line_id,
                    scheduled_departure_time=scheduled_departure,
                    scheduled_wakeup_time=scheduled_wakeup,
                )
                self.upsert_departure_record(record)
                continue

            _, record = found

            # 出発予定時間と起床予定時間を一度に更新（無駄なAPI呼び出しを避ける）
            updated = False

            # 出発予定時間の自動設定
            if record.scheduled_departure_time is None:
                if cast.default_departure_time:
                    record.scheduled_departure_time = cast.default_departure_time
                    updated = True
                else:
                    missing_departure.append(cast.name)

            # 起床予定時間の自動設定（起床予定時間がONのキャストのみ）
            if cast.wakeup_time_registration_enabled and record.scheduled_wakeup_time is None:
                if cast.default_wakeup_time:
                    record.scheduled_wakeup_time = cast.default_wakeup_time
                    updated = True
                else:
                    missing_wakeup.append(cast.name)

            if updated:
                self.upsert_departure_record(record)

        return missing_departure, missing_wakeup

    def _row_to_record(self, data: dict) -> Optional[DepartureRecord]:
        """行データをDepartureRecordに変換"""
        try:
            # 出発予定時間
            scheduled_departure = None
            if data.get("出発予定時間"):
                parts = data["出発予定時間"].split(":")
                if len(parts) >= 2:
                    scheduled_departure = time(int(parts[0]), int(parts[1]))

            # 出発報告時刻
            actual_departure = None
            if data.get("出発報告時刻"):
                actual_departure = self._ensure_timezone(
                    datetime.fromisoformat(data["出発報告時刻"])
                )

            # 出発判定
            departure_status = None
            if data.get("出発判定"):
                departure_status = DepartureStatus(data["出発判定"])

            # 起床予定時間
            scheduled_wakeup = None
            if data.get("起床予定時間"):
                parts = data["起床予定時間"].split(":")
                if len(parts) >= 2:
                    scheduled_wakeup = time(int(parts[0]), int(parts[1]))

            # 起床報告時刻
            actual_wakeup = None
            if data.get("起床報告時刻"):
                actual_wakeup = self._ensure_timezone(
                    datetime.fromisoformat(data["起床報告時刻"])
                )

            # 起床判定
            wakeup_status = None
            if data.get("起床判定"):
                wakeup_status = WakeupStatus(data["起床判定"])

            # 最終結果
            final_result = None
            if data.get("最終結果"):
                final_result = FinalResult(data["最終結果"])

            record = DepartureRecord(
                date=data.get("日付", ""),
                name=data.get("氏名", ""),
                line_id=data.get("LINE_ID", ""),
                scheduled_departure_time=scheduled_departure,
                actual_departure_time=actual_departure,
                departure_status=departure_status,
                departure_phone_call_count=int(data.get("出発電話発信回数") or 0),
                scheduled_wakeup_time=scheduled_wakeup,
                actual_wakeup_time=actual_wakeup,
                wakeup_status=wakeup_status,
                wakeup_phone_call_count=int(data.get("起床電話発信回数") or 0),
                final_result=final_result,
            )
            return record
        except Exception as exc:
            self._logger.warning("Invalid departure record skipped: %s", exc)
            return None

    def _record_to_row(self, record: DepartureRecord) -> List[str]:
        """DepartureRecordを行データに変換"""
        return [
            record.date,
            record.name,
            record.line_id,
            record.scheduled_departure_time.strftime("%H:%M") if record.scheduled_departure_time else "",
            record.actual_departure_time.isoformat(sep=" ") if record.actual_departure_time else "",
            record.departure_status.value if record.departure_status else "",
            str(record.departure_phone_call_count),
            record.scheduled_wakeup_time.strftime("%H:%M") if record.scheduled_wakeup_time else "",
            record.actual_wakeup_time.isoformat(sep=" ") if record.actual_wakeup_time else "",
            record.wakeup_status.value if record.wakeup_status else "",
            str(record.wakeup_phone_call_count),
            record.final_result.value if record.final_result else "",
        ]

    def _ensure_timezone(self, value: datetime) -> datetime:
        """タイムゾーンを付与"""
        if value.tzinfo is None:
            return value.replace(tzinfo=self._tz)
        return value.astimezone(self._tz)
