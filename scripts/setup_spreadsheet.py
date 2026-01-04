"""スプレッドシートセットアップスクリプト

Google Sheetsに必要なシートと列ヘッダーを作成します。
"""
import json
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .envファイルを読み込む
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# スプレッドシートID
SPREADSHEET_ID = "1bkncXLAnKVRAPLDtA4lzZAu_VQUbZkS8P6dkVcz353Q"

# シート定義
SHEETS = {
    "キャスト一覧": [
        "氏名",
        "LINE_ID",
        "電話番号",
        "通常出発予定時間",
        "起床予定時間登録ON/OFF",
        "通常起床予定時間",
        "起床オフセット（分）",
    ],
    "出発予定時間_当日管理": [
        "日付",
        "氏名",
        "LINE_ID",
        "出発予定時間",
        "出発報告時刻",
        "出発判定",
        "出発電話発信回数",
        "起床予定時間",
        "起床報告時刻",
        "起床判定",
        "起床電話発信回数",
        "最終結果",
    ],
}


def get_sheets_service():
    """Google Sheets APIサービスを取得"""
    creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
    if not creds_json:
        raise ValueError("GOOGLE_SHEETS_CREDENTIALS_JSON environment variable not set")

    creds_data = json.loads(creds_json)
    credentials = Credentials.from_service_account_info(
        creds_data,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=credentials)


def get_existing_sheets(service) -> dict:
    """既存のシート情報を取得"""
    result = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = {}
    for sheet in result.get("sheets", []):
        props = sheet.get("properties", {})
        sheets[props.get("title")] = props.get("sheetId")
    return sheets


def create_sheet(service, sheet_name: str) -> int:
    """新しいシートを作成"""
    request = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": sheet_name,
                    }
                }
            }
        ]
    }
    result = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=request
    ).execute()
    return result["replies"][0]["addSheet"]["properties"]["sheetId"]


def set_headers(service, sheet_name: str, headers: list):
    """ヘッダー行を設定"""
    range_name = f"'{sheet_name}'!A1:{chr(64 + len(headers))}1"
    body = {"values": [headers]}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption="RAW",
        body=body,
    ).execute()


def freeze_header_row(service, sheet_id: int):
    """ヘッダー行を固定"""
    request = {
        "requests": [
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=request
    ).execute()


def format_header_row(service, sheet_id: int, num_columns: int):
    """ヘッダー行の書式設定（太字、背景色）"""
    request = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": num_columns,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.9,
                                "green": 0.9,
                                "blue": 0.9,
                            },
                            "textFormat": {"bold": True},
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat)",
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=request
    ).execute()


def main():
    """メイン処理"""
    print("=" * 50)
    print("Spreadsheet Setup")
    print("=" * 50)
    print()

    # サービス取得
    print("[1] Connecting to Google Sheets API...")
    try:
        service = get_sheets_service()
        print("  Connection successful")
    except Exception as e:
        print(f"  Connection failed: {e}")
        sys.exit(1)
    print()

    # 既存シート確認
    print("[2] Checking existing sheets...")
    existing_sheets = get_existing_sheets(service)
    print(f"  Found {len(existing_sheets)} sheet(s): {list(existing_sheets.keys())}")
    print()

    # 各シートをセットアップ
    for idx, (sheet_name, headers) in enumerate(SHEETS.items(), start=3):
        print(f"[{idx}] Setting up '{sheet_name}'...")

        if sheet_name in existing_sheets:
            print(f"  Sheet already exists (ID: {existing_sheets[sheet_name]})")
            sheet_id = existing_sheets[sheet_name]
        else:
            print("  Creating new sheet...")
            sheet_id = create_sheet(service, sheet_name)
            print(f"  Sheet created (ID: {sheet_id})")

        # ヘッダー設定
        print(f"  Setting headers ({len(headers)} columns)...")
        set_headers(service, sheet_name, headers)
        print("  Headers set")

        # ヘッダー行固定
        print("  Freezing header row...")
        freeze_header_row(service, sheet_id)
        print("  Header row frozen")

        # ヘッダー行書式設定
        print("  Formatting header row...")
        format_header_row(service, sheet_id, len(headers))
        print("  Header row formatted")

        print()

    print("=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print()
    print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
    print()
    print("Created sheets:")
    for sheet_name, headers in SHEETS.items():
        print(f"  - {sheet_name} ({len(headers)} columns)")


if __name__ == "__main__":
    main()
