# おはよう和子さん - デプロイ準備チェックリスト

**作成日**: 2026年1月4日

---

## デプロイ前チェックリスト

### ✅ 1. 環境構築

- [ ] Python 3.11+がインストールされている
- [ ] 仮想環境が作成されている
- [ ] 依存パッケージがインストールされている
- [ ] ログディレクトリが作成されている

### ✅ 2. 環境変数の設定

#### 必須環境変数
- [ ] `LINE_CHANNEL_ACCESS_TOKEN` - LINE Messaging APIアクセストークン
- [ ] `LINE_CHANNEL_SECRET` - LINE Messaging APIシークレット
- [ ] `TWILIO_ACCOUNT_SID` - TwilioアカウントSID
- [ ] `TWILIO_AUTH_TOKEN` - Twilio認証トークン
- [ ] `TWILIO_PHONE_NUMBER` - Twilio電話番号（E.164形式、例: +819012345678）
- [ ] `GOOGLE_SHEETS_CREDENTIALS_JSON` - Google Sheets認証情報（JSON形式）
- [ ] `GOOGLE_SHEETS_SPREADSHEET_ID` - Google SheetsスプレッドシートID
- [ ] `CONTROL_LINE_ID` - 管制LINE ID

#### オプション環境変数
- [ ] `TAKAGI_LINE_ID` - 髙木LINE ID（Procast未取得通知用）
- [ ] `SLACK_WEBHOOK_URL` - Slack Webhook URL（エラー通知用）
- [ ] `GOOGLE_DRIVE_CREDENTIALS_JSON` - Google Drive認証情報（Procastデータ取得用）
- [ ] `GOOGLE_DRIVE_PROCAST_FOLDER_ID` - ProcastデータフォルダID
- [ ] `GOOGLE_DRIVE_PROCAST_FILE_NAME` - Procastデータファイル名（デフォルト: procast_data.csv）
- [ ] `TZ` - タイムゾーン（デフォルト: Asia/Tokyo）
- [ ] `LOG_LEVEL` - ログレベル（デフォルト: INFO）
- [ ] `LOG_FILE` - ログファイルパス（デフォルト: ./logs/app.log）

### ✅ 3. Google Sheetsの準備

#### キャスト一覧シート
- [ ] シート名: `キャスト一覧`
- [ ] 列の設定:
  - [ ] 氏名
  - [ ] LINE_ID
  - [ ] 電話番号（+81形式）
  - [ ] 通常出発予定時間（HH:MM形式、5分単位）
  - [ ] 起床予定時間登録ON/OFF（TRUE/FALSE）
  - [ ] 通常起床予定時間（HH:MM形式、5分単位）
  - [ ] 起床オフセット（分）

#### 出発予定時間_当日管理シート
- [ ] シート名: `出発予定時間_当日管理`
- [ ] 列の設定:
  - [ ] 日付（YYYY-MM-DD形式）
  - [ ] 氏名
  - [ ] LINE_ID
  - [ ] 出発予定時間（HH:MM形式）
  - [ ] 出発報告時刻（ISO8601形式）
  - [ ] 出発判定（OK/遅れ返/要確認）
  - [ ] 出発電話発信回数（数値）
  - [ ] 起床予定時間（HH:MM形式）
  - [ ] 起床報告時刻（ISO8601形式）
  - [ ] 起床判定（OK/遅れ返/要確認）
  - [ ] 起床電話発信回数（数値）
  - [ ] 最終結果（OK/要管制）

#### 権限設定
- [ ] サービスアカウントにスプレッドシートへの編集権限が付与されている

### ✅ 4. LINE Messaging APIの設定

- [ ] LINE Developers Consoleでチャンネルが作成されている
- [ ] チャンネルアクセストークンを取得している
- [ ] チャンネルシークレットを取得している
- [ ] Webhook URLを設定する準備ができている（デプロイ後に設定）

### ✅ 5. Twilioの設定

- [ ] Twilioアカウントが作成されている
- [ ] アカウントSIDを取得している
- [ ] 認証トークンを取得している
- [ ] 電話番号を取得している（E.164形式）
- [ ] アカウントに十分な残高がある

### ✅ 6. Google Cloud Platformの設定

- [ ] Google Cloud Platformプロジェクトが作成されている
- [ ] Google Sheets APIが有効化されている
- [ ] Google Drive APIが有効化されている（Procastデータ取得用）
- [ ] サービスアカウントが作成されている
- [ ] サービスアカウントの認証情報（JSON）を取得している

### ✅ 7. セットアップ確認

- [ ] `python scripts/verify_setup.py` を実行して確認
- [ ] すべての必須環境変数が設定されている
- [ ] Google Sheetsへの接続が成功している
- [ ] ログディレクトリが作成されている

### ✅ 8. デプロイ準備

- [ ] アプリケーションが起動できることを確認
- [ ] ヘルスチェックエンドポイントが動作することを確認
- [ ] ログ出力が正常に動作することを確認

---

## デプロイ手順

### 1. 環境変数の設定

```bash
cp .env.example .env
# .envファイルを編集して実際の値を設定
```

### 2. セットアップ確認

```bash
python scripts/verify_setup.py
```

### 3. アプリケーションの起動

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. ヘルスチェック

```bash
curl http://localhost:8000/health
```

期待されるレスポンス:
```json
{"status": "healthy", "timestamp": "2024-01-01T00:00:00+09:00"}
```

### 5. LINE Webhook URLの設定

LINE Developers Consoleで、Webhook URLを設定:
```
https://your-domain.com/webhook/line
```

---

## デプロイ後の確認事項

### 動作確認

- [ ] ヘルスチェックが正常に動作する
- [ ] LINE Botにメッセージを送信して応答がある
- [ ] 出発予定時間の登録が正常に動作する
- [ ] 起床予定時間の登録が正常に動作する
- [ ] リマインド通知が正常に送信される
- [ ] スケジューラーが正常に動作する

### ログ確認

- [ ] ログファイルが作成されている
- [ ] エラーログがない
- [ ] 正常な動作ログが記録されている

---

## トラブルシューティング

### 環境変数エラー

```
RuntimeError: Missing required env vars: ...
```

→ `.env`ファイルに必要な環境変数が設定されているか確認

### Google Sheets接続エラー

```
googleapiclient.errors.HttpError: 403 ...
```

→ サービスアカウントにスプレッドシートへのアクセス権限があるか確認

### LINE Webhookエラー

```
HTTPException: 400 Invalid signature
```

→ チャンネルシークレットが正しいか確認

### Twilio電話発信エラー

```
TwilioRestException: ...
```

→ アカウントSID、認証トークン、電話番号が正しいか確認

---

**作成日**: 2026年1月4日  
**最終更新日**: 2026年1月4日

