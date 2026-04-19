"""Procastデータ取得サービス"""
import csv
import io
import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from zoneinfo import ZoneInfo

from app.config import Settings
from app.utils.logger import get_logger


class ProcastService:
    """Procastデータ取得サービス"""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = get_logger("procast_service")
        self._tz = ZoneInfo(settings.tz)
        self._data: Optional[Dict[str, Any]] = None
        self._data_date: Optional[date] = None

        # Google Drive API初期化
        if settings.google_drive_credentials_json:
            creds_info = json.loads(settings.google_drive_credentials_json)
            creds = Credentials.from_service_account_info(
                creds_info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
            self._drive_service = build("drive", "v3", credentials=creds, cache_discovery=False)
        else:
            self._drive_service = None

    def has_data(self) -> bool:
        """データが取得済みか確認"""
        if self._data is None:
            return False
        # 当日のデータかどうかも確認
        today = datetime.now(self._tz).date()
        return self._data_date == today

    def get_data(self) -> Optional[Dict[str, Any]]:
        """取得済みデータを返す"""
        return self._data

    async def fetch_procast_data(self) -> Optional[Dict[str, Any]]:
        """
        Google DriveからProcastデータを取得

        Returns:
            取得したデータ（辞書形式）、失敗時はNone
        """
        if not self._drive_service:
            self._logger.warning("Google Drive service not initialized")
            return None

        if not self._settings.google_drive_procast_folder_id:
            self._logger.warning("GOOGLE_DRIVE_PROCAST_FOLDER_ID not set")
            return None

        try:
            # フォルダ内のファイルを検索
            file_name = self._settings.google_drive_procast_file_name
            query = (
                f"'{self._settings.google_drive_procast_folder_id}' in parents "
                f"and name = '{file_name}' "
                f"and trashed = false"
            )

            results = self._drive_service.files().list(
                q=query,
                spaces="drive",
                fields="files(id, name, modifiedTime)",
                orderBy="modifiedTime desc",
                pageSize=1,
            ).execute()

            files = results.get("files", [])
            if not files:
                self._logger.warning("Procast file not found: %s", file_name)
                return None

            file_id = files[0]["id"]
            file_name = files[0]["name"]
            self._logger.info("Found Procast file: %s (id=%s)", file_name, file_id)

            # ファイルをダウンロード
            request = self._drive_service.files().get_media(fileId=file_id)
            content = io.BytesIO()
            downloader = MediaIoBaseDownload(content, request)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            content.seek(0)

            # ファイル形式に応じてパース
            data = self._parse_file(content, file_name)

            if data:
                self._data = data
                self._data_date = datetime.now(self._tz).date()
                self._logger.info("Procast data loaded successfully")
                return data

            return None

        except Exception as exc:
            self._logger.error("Failed to fetch Procast data: %s", exc)
            return None

    def _parse_file(self, content: io.BytesIO, file_name: str) -> Optional[Dict[str, Any]]:
        """
        ファイルをパース

        Args:
            content: ファイルコンテンツ
            file_name: ファイル名（拡張子判定用）

        Returns:
            パースしたデータ
        """
        try:
            file_name_lower = file_name.lower()
            if file_name_lower.endswith(".csv"):
                return self._parse_csv(content)
            elif file_name_lower.endswith(".json"):
                return self._parse_json(content)
            else:
                self._logger.warning("Unsupported file format: %s", file_name)
                return None
        except Exception as exc:
            self._logger.error("Failed to parse file: %s", exc)
            return None

    def _parse_csv(self, content: io.BytesIO) -> Dict[str, Any]:
        """CSVファイルをパース"""
        text = content.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        return {
            "format": "csv",
            "rows": rows,
            "working_casts": self._extract_working_casts(rows),
        }

    def _parse_json(self, content: io.BytesIO) -> Optional[Dict[str, Any]]:
        """JSONファイルをパース"""
        try:
            text = content.read().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            self._logger.error("Failed to decode JSON file: %s", exc)
            return None
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            self._logger.error("Failed to parse JSON content: %s", exc)
            return None
        if isinstance(data, list):
            return {
                "format": "json",
                "rows": data,
                "working_casts": self._extract_working_casts(data),
            }
        return data

    def _extract_working_casts(self, rows: List[Dict[str, Any]]) -> Set[str]:
        """
        翌日出勤のキャストを抽出

        Note:
            ファイル形式が確定していないため、複数のカラム名をサポート
        """
        working = set()
        if not rows:
            return working
        tomorrow = (datetime.now(self._tz) + timedelta(days=1)).date()

        for row in rows:
            # 複数のカラム名をサポート
            name = row.get("氏名") or row.get("name") or row.get("キャスト名") or ""
            work_date = row.get("日付") or row.get("date") or row.get("出勤日") or ""
            is_working = row.get("出勤") or row.get("working") or row.get("出勤あり") or ""

            # 日付が翌日かつ出勤ありの場合
            if work_date:
                try:
                    if isinstance(work_date, str):
                        parsed_date = date.fromisoformat(work_date.split("T")[0])
                    else:
                        parsed_date = work_date
                    if parsed_date == tomorrow:
                        if str(is_working).upper() in ("TRUE", "1", "あり", "○", "YES"):
                            if name:  # 空文字列名はスキップ
                                working.add(name)
                except ValueError:
                    pass

        return working

    def is_cast_working_tomorrow(self, name: str) -> bool:
        """
        キャストが翌日出勤かどうか判定

        Args:
            name: キャスト名

        Returns:
            翌日出勤の場合True、それ以外はFalse
            データがない場合もFalse（リマインドをスキップするため）
        """
        if not self._data:
            return False

        working_casts = self._data.get("working_casts", set())
        return name in working_casts

    def get_working_casts_tomorrow(self) -> Set[str]:
        """翌日出勤のキャスト一覧を取得"""
        if not self._data:
            return set()
        return self._data.get("working_casts", set())

    def clear_data(self) -> None:
        """データをクリア"""
        self._data = None
        self._data_date = None
