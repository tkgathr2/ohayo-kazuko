import json
from datetime import date, datetime, time
from typing import List, Optional, Tuple

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from zoneinfo import ZoneInfo

from app.config import Settings
from app.models import Cast, DepartureRecord, DepartureStatus, FinalResult
from app.utils.logger import get_logger


CAST_SHEET = "キャスト一覧"
DEPARTURE_SHEET = "出発見守り_当日管理"


class SpreadsheetService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = get_logger("spreadsheet_service")
        self._tz = ZoneInfo(settings.tz)
        creds_info = json.loads(settings.google_sheets_credentials_json)
        creds = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        self._service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    def _get_values(self, sheet_name: str) -> List[List[str]]:
        result = (
            self._service.spreadsheets()
            .values()
            .get(spreadsheetId=self._settings.google_sheets_spreadsheet_id, range=sheet_name)
            .execute()
        )
        return result.get("values", [])

    def _update_values(self, range_name: str, values: List[List[str]]) -> None:
        body = {"values": values}
        (
            self._service.spreadsheets()
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
        body = {"values": values}
        (
            self._service.spreadsheets()
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
        rows = self._get_values(CAST_SHEET)
        if not rows:
            return []
        header = rows[0]
        casts: List[Cast] = []
        for row in rows[1:]:
            data = dict(zip(header, row))
            try:
                default_time = None
                if data.get("通常出発予定時間"):
                    hour, minute = data["通常出発予定時間"].split(":")
                    default_time = time(int(hour), int(minute))
                cast = Cast(
                    name=data.get("氏名", ""),
                    line_id=data.get("LINE_ID", ""),
                    phone_number=data.get("電話番号", ""),
                    default_departure_time=default_time,
                    department=data.get("所属"),
                    notes=data.get("備考"),
                )
                casts.append(cast)
            except Exception as exc:
                self._logger.warning("Invalid cast row skipped: %s", exc)
        return casts

    def get_departure_records(self, target_date: date) -> List[DepartureRecord]:
        rows = self._get_values(DEPARTURE_SHEET)
        if not rows:
            return []
        header = rows[0]
        records: List[DepartureRecord] = []
        for row in rows[1:]:
            data = dict(zip(header, row))
            if data.get("日付") != target_date.isoformat():
                continue
            record = self._row_to_record(data)
            if record:
                records.append(record)
        return records

    def get_departure_record(self, target_date: date, line_id: str) -> Optional[Tuple[int, DepartureRecord]]:
        rows = self._get_values(DEPARTURE_SHEET)
        if not rows:
            return None
        header = rows[0]
        for index, row in enumerate(rows[1:], start=2):
            data = dict(zip(header, row))
            if data.get("日付") == target_date.isoformat() and data.get("LINE_ID") == line_id:
                record = self._row_to_record(data)
                if record:
                    return index, record
        return None

    def upsert_departure_record(self, record: DepartureRecord) -> None:
        found = self.get_departure_record(record.date, record.line_id)
        if found:
            row_index, _ = found
            range_name = f"{DEPARTURE_SHEET}!A{row_index}:I{row_index}"
            self._update_values(range_name, [self._record_to_row(record)])
            return
        self._append_values(f"{DEPARTURE_SHEET}!A:I", [self._record_to_row(record)])

    def update_departure_actual_time(self, target_date: date, line_id: str, actual_time: datetime) -> None:
        found = self.get_departure_record(target_date, line_id)
        if not found:
            return
        row_index, record = found
        record.actual_departure_time = actual_time
        self.upsert_departure_record(record)

    def update_departure_status(self, target_date: date, line_id: str, status: DepartureStatus) -> None:
        found = self.get_departure_record(target_date, line_id)
        if not found:
            return
        row_index, record = found
        record.departure_status = status
        self.upsert_departure_record(record)

    def auto_assign_default_times(self, target_date: date) -> List[str]:
        casts = {cast.line_id: cast for cast in self.get_casts()}
        missing = []
        for line_id, cast in casts.items():
            found = self.get_departure_record(target_date, line_id)
            if not found:
                if cast.default_departure_time is None:
                    missing.append(cast.name)
                    continue
                scheduled = datetime.combine(target_date, cast.default_departure_time, tzinfo=self._tz)
                record = DepartureRecord(
                    date=target_date,
                    name=cast.name,
                    line_id=cast.line_id,
                    scheduled_departure_time=scheduled,
                )
                self.upsert_departure_record(record)
                continue
            _, record = found
            if record.scheduled_departure_time is None:
                if cast.default_departure_time is None:
                    missing.append(cast.name)
                    continue
                record.scheduled_departure_time = datetime.combine(target_date, cast.default_departure_time, tzinfo=self._tz)
                self.upsert_departure_record(record)
        return missing

    def _row_to_record(self, data: dict) -> Optional[DepartureRecord]:
        try:
            scheduled = None
            if data.get("出発予定時間"):
                scheduled = self._ensure_timezone(datetime.fromisoformat(data["出発予定時間"]))
            actual = None
            if data.get("出発時間"):
                actual = self._ensure_timezone(datetime.fromisoformat(data["出発時間"]))
            status = data.get("出発判定") or None
            final = data.get("最終結果") or None
            record = DepartureRecord(
                date=date.fromisoformat(data.get("日付")),
                name=data.get("氏名", ""),
                line_id=data.get("LINE_ID", ""),
                scheduled_departure_time=scheduled,
                actual_departure_time=actual,
                departure_status=DepartureStatus(status) if status else None,
                phone_call_count=int(data.get("出発電話回数", 0) or 0),
                final_result=FinalResult(final) if final else None,
                control_notes=data.get("管制メモ"),
            )
            return record
        except Exception as exc:
            self._logger.warning("Invalid departure record skipped: %s", exc)
            return None

    def _record_to_row(self, record: DepartureRecord) -> List[str]:
        return [
            record.date.isoformat(),
            record.name,
            record.line_id,
            record.scheduled_departure_time.isoformat(sep=" ") if record.scheduled_departure_time else "",
            record.actual_departure_time.isoformat(sep=" ") if record.actual_departure_time else "",
            record.departure_status.value if record.departure_status else "",
            str(record.phone_call_count),
            record.final_result.value if record.final_result else "",
            record.control_notes or "",
        ]

    def _ensure_timezone(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=self._tz)
        return value.astimezone(self._tz)
