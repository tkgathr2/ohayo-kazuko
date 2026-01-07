# 環境変数テンプレート

このファイルを参考に、`.env`ファイルを作成してください。

```bash
# プロジェクトルートで実行
cp docs/ENV_TEMPLATE.md .env
# .envファイルを編集して実際の値を設定
```

---

## 環境変数設定

```env
# おはよう和子さん - 環境変数設定
# このファイルを .env として保存し、実際の値を設定してください

# ============================================
# 必須環境変数
# ============================================

# LINE Messaging API
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
LINE_CHANNEL_SECRET=your_line_channel_secret_here

# Twilio Voice API
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+819012345678

# Google Sheets API
GOOGLE_SHEETS_CREDENTIALS_JSON={"type": "service_account", "project_id": "your-project-id", ...}
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here

# 管制LINE ID
CONTROL_LINE_ID=Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# オプション環境変数
# ============================================

# 髙木LINE ID（Procast未取得通知用）
TAKAGI_LINE_ID=Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Slack Webhook（エラー通知用）
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Google Drive API（Procastデータ取得用）
GOOGLE_DRIVE_CREDENTIALS_JSON={"type": "service_account", "project_id": "your-project-id", ...}
GOOGLE_DRIVE_PROCAST_FOLDER_ID=your_folder_id_here
GOOGLE_DRIVE_PROCAST_FILE_NAME=procast_data.csv

# タイムゾーン
TZ=Asia/Tokyo

# ログ設定
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# API設定
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 環境変数の説明

### 必須環境変数

| 変数名 | 説明 | 取得方法 |
|--------|------|----------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging APIのチャンネルアクセストークン | LINE Developers Console |
| `LINE_CHANNEL_SECRET` | LINE Messaging APIのチャンネルシークレット | LINE Developers Console |
| `TWILIO_ACCOUNT_SID` | TwilioアカウントSID | Twilio Console |
| `TWILIO_AUTH_TOKEN` | Twilio認証トークン | Twilio Console |
| `TWILIO_PHONE_NUMBER` | Twilio電話番号（E.164形式） | Twilio Console |
| `GOOGLE_SHEETS_CREDENTIALS_JSON` | Google Sheets認証情報（JSON形式） | Google Cloud Console |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | Google SheetsスプレッドシートID | Google Sheets URL |
| `CONTROL_LINE_ID` | 管制LINE ID | LINE Botから取得 |

### オプション環境変数

| 変数名 | 説明 | デフォルト |
|--------|------|------------|
| `TAKAGI_LINE_ID` | 髙木LINE ID（Procast未取得通知用） | - |
| `SLACK_WEBHOOK_URL` | Slack Webhook URL（エラー通知用） | - |
| `GOOGLE_DRIVE_CREDENTIALS_JSON` | Google Drive認証情報 | - |
| `GOOGLE_DRIVE_PROCAST_FOLDER_ID` | ProcastデータフォルダID | - |
| `GOOGLE_DRIVE_PROCAST_FILE_NAME` | Procastデータファイル名 | procast_data.csv |
| `TZ` | タイムゾーン | Asia/Tokyo |
| `LOG_LEVEL` | ログレベル | INFO |
| `LOG_FILE` | ログファイルパス | ./logs/app.log |
| `API_HOST` | APIホスト | 0.0.0.0 |
| `API_PORT` | APIポート | 8000 |

---

## 設定手順

1. プロジェクトルートに`.env`ファイルを作成
2. 上記のテンプレートをコピー
3. 各環境変数に実際の値を設定
4. セットアップ確認スクリプトを実行:
   ```bash
   python scripts/verify_setup.py
   ```

---

**注意**: `.env`ファイルは`.gitignore`に含まれているため、Gitにコミットされません。本番環境では、環境変数を直接設定するか、安全な方法で管理してください。

