# デプロイ手順書

## 前提条件

- Python 3.11以上
- LINE Messaging APIチャンネル
- Twilioアカウント
- Google Cloud Platformプロジェクト（Sheets API、Drive API有効化）
- Slack Workspace（オプション、エラー通知用）

## デプロイ手順

### 1. コードの取得

```bash
git clone <repository-url>
cd kazuko_departure_watch
```

### 2. 依存パッケージのインストール

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集し、以下の環境変数を設定してください：

#### 必須環境変数

| 変数名 | 説明 |
|--------|------|
| LINE_CHANNEL_ACCESS_TOKEN | LINE Messaging APIのチャンネルアクセストークン |
| LINE_CHANNEL_SECRET | LINE Messaging APIのチャンネルシークレット |
| TWILIO_ACCOUNT_SID | TwilioアカウントSID |
| TWILIO_AUTH_TOKEN | Twilio認証トークン |
| TWILIO_PHONE_NUMBER | Twilio電話番号（+81形式） |
| GOOGLE_SHEETS_CREDENTIALS_JSON | Google APIサービスアカウントの認証情報（JSON形式） |
| GOOGLE_SHEETS_SPREADSHEET_ID | Google SheetsのスプレッドシートID |
| CONTROL_LINE_ID | 管制のLINEユーザーID |

#### オプション環境変数

| 変数名 | 説明 | デフォルト |
|--------|------|------------|
| TAKAGI_LINE_ID | 髙木のLINEユーザーID（Procast未取得通知用） | - |
| SLACK_WEBHOOK_URL | Slack Webhook URL（エラー通知用） | - |
| GOOGLE_DRIVE_CREDENTIALS_JSON | Google Drive API認証情報 | - |
| GOOGLE_DRIVE_PROCAST_FOLDER_ID | ProcastデータのフォルダID | - |
| GOOGLE_DRIVE_PROCAST_FILE_NAME | Procastデータのファイル名 | procast_data.csv |
| TZ | タイムゾーン | Asia/Tokyo |
| LOG_LEVEL | ログレベル | INFO |
| LOG_FILE | ログファイルパス | ./logs/app.log |

### 4. Google Sheetsの準備

以下のシートを作成してください：

#### キャスト一覧

| 列名 | 説明 |
|------|------|
| 氏名 | キャストの氏名 |
| LINE_ID | LINEユーザーID |
| 電話番号 | 電話番号（+81形式） |
| 通常出発予定時間 | HH:MM形式 |
| 起床予定時間登録ON/OFF | TRUE/FALSE |
| 通常起床予定時間 | HH:MM形式 |
| 起床オフセット（分） | 数値 |

#### 出発予定時間_当日管理

| 列名 | 説明 |
|------|------|
| 日付 | YYYY-MM-DD |
| 氏名 | キャストの氏名 |
| LINE_ID | LINEユーザーID |
| 出発予定時間 | HH:MM |
| 出発報告時刻 | ISO8601形式 |
| 出発判定 | OK/遅れ返/要確認 |
| 出発電話発信回数 | 数値 |
| 起床予定時間 | HH:MM |
| 起床報告時刻 | ISO8601形式 |
| 起床判定 | OK/遅れ返/要確認 |
| 起床電話発信回数 | 数値 |
| 最終結果 | OK/要管制 |

### 5. ログディレクトリの作成

```bash
mkdir -p logs
```

### 6. セットアップの確認

```bash
python scripts/verify_setup.py
```

### 7. アプリケーションの起動

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### systemdサービスとして実行（Linux）

```ini
[Unit]
Description=Ohayo Kazuko-san
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/kazuko_departure_watch
Environment="PATH=/path/to/kazuko_departure_watch/.venv/bin"
ExecStart=/path/to/kazuko_departure_watch/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 動作確認

### 1. ヘルスチェック

```bash
curl http://localhost:8000/health
```

期待されるレスポンス：
```json
{"status": "healthy", "timestamp": "2024-01-01T00:00:00+09:00"}
```

### 2. LINE Webhookの設定

LINE Developersコンソールで、Webhook URLを設定：
```
https://your-domain.com/webhook/line
```

### 3. テストメッセージの送信

LINE Botに以下のメッセージを送信：
- `出発 08:30` - 出発予定時間の登録
- `起床 07:00` - 起床予定時間の登録

## トラブルシューティング

### 環境変数エラー

```
RuntimeError: Missing required env vars: ...
```

`.env`ファイルに必要な環境変数が設定されているか確認してください。

### Google Sheets接続エラー

```
googleapiclient.errors.HttpError: 403 ...
```

- サービスアカウントにスプレッドシートへのアクセス権限があるか確認
- スプレッドシートIDが正しいか確認

### LINE Webhookエラー

```
HTTPException: 400 Invalid signature
```

- チャンネルシークレットが正しいか確認
- リクエストボディが改変されていないか確認

### Twilio電話発信エラー

```
TwilioRestException: ...
```

- アカウントSIDと認証トークンが正しいか確認
- 電話番号がE.164形式（+81...）か確認
- アカウントに十分な残高があるか確認

## ログの確認

```bash
# リアルタイムログ
tail -f logs/app.log

# エラーログのみ
grep ERROR logs/app.log
```

## バックアップ

定期的に以下をバックアップしてください：

- `.env`ファイル
- Google Sheetsのデータ
- `logs/`ディレクトリ
