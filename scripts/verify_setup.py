"""セットアップ確認スクリプト"""
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_env_vars() -> bool:
    """必須環境変数の確認"""
    required_vars = [
        "LINE_CHANNEL_ACCESS_TOKEN",
        "LINE_CHANNEL_SECRET",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "GOOGLE_SHEETS_CREDENTIALS_JSON",
        "GOOGLE_SHEETS_SPREADSHEET_ID",
        "CONTROL_LINE_ID",
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"  Missing: {', '.join(missing)}")
        return False

    print("  All required environment variables are set")
    return True


def check_optional_env_vars() -> bool:
    """オプション環境変数の確認"""
    optional_vars = [
        ("TAKAGI_LINE_ID", "Procastデータ未取得通知"),
        ("SLACK_WEBHOOK_URL", "Slackエラー通知"),
        ("GOOGLE_DRIVE_CREDENTIALS_JSON", "Procastデータ取得"),
        ("GOOGLE_DRIVE_PROCAST_FOLDER_ID", "Procastデータ取得"),
    ]

    configured = []
    not_configured = []

    for var, desc in optional_vars:
        if os.getenv(var):
            configured.append(f"{var} ({desc})")
        else:
            not_configured.append(f"{var} ({desc})")

    if configured:
        print(f"  Configured: {len(configured)}")
        for v in configured:
            print(f"    - {v}")

    if not_configured:
        print(f"  Not configured: {len(not_configured)}")
        for v in not_configured:
            print(f"    - {v}")

    return True


def check_google_sheets() -> bool:
    """Google Sheetsへの接続確認"""
    try:
        from app.config import get_settings
        from app.services.spreadsheet_service import SpreadsheetService

        settings = get_settings()
        service = SpreadsheetService(settings)
        casts = service.get_casts()

        print(f"  Connection successful (casts: {len(casts)})")
        return True
    except Exception as e:
        print(f"  Connection failed: {e}")
        return False


def check_log_directory() -> bool:
    """ログディレクトリの確認"""
    log_dir = project_root / "logs"

    if log_dir.exists():
        print(f"  Log directory exists: {log_dir}")
        return True
    else:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            print(f"  Log directory created: {log_dir}")
            return True
        except Exception as e:
            print(f"  Failed to create log directory: {e}")
            return False


def main() -> None:
    """メイン処理"""
    print("=" * 50)
    print("Setup Verification")
    print("=" * 50)
    print()

    results = []

    print("[1] Required Environment Variables")
    results.append(("Required Env Vars", check_env_vars()))
    print()

    print("[2] Optional Environment Variables")
    results.append(("Optional Env Vars", check_optional_env_vars()))
    print()

    print("[3] Log Directory")
    results.append(("Log Directory", check_log_directory()))
    print()

    # Google Sheetsは環境変数が設定されている場合のみ確認
    if os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON") and os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID"):
        print("[4] Google Sheets Connection")
        results.append(("Google Sheets", check_google_sheets()))
        print()

    print("=" * 50)
    print("Results")
    print("=" * 50)

    all_required_ok = True
    for name, result in results:
        status = "OK" if result else "FAILED"
        print(f"  {name}: {status}")
        if name == "Required Env Vars" and not result:
            all_required_ok = False

    print()

    if all_required_ok:
        print("Setup verification completed successfully.")
        sys.exit(0)
    else:
        print("Setup verification failed. Please check the missing items.")
        sys.exit(1)


if __name__ == "__main__":
    main()
