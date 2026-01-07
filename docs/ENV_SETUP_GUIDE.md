# 環境変数設定ガイド

このガイドは`.env`ファイルを作成し、必要な環境変数を設定する手順を説明します。

## 前提条件

以下のファイルが準備されていることを確認してください：

- `credentials/credentials_oneline.txt`: Google Cloud Platform サービスアカウントキー（1行形式）

## 手順

### 1. .envファイルの作成

プロジェクトルートで以下のコマンドを実行：

```bash
cp .env.example .env
```

### 2. 環境変数の設定

`.env`ファイルを開き、以下の環境変数を設定してください。

#### 必須環境変数

##### LINE Messaging API

```env
LINE_CHANNEL_ACCESS_TOKEN=<LINE Developers Consoleから取得>
LINE_CHANNEL_SECRET=<LINE Developers Consoleから取得>
```

##### Twilio Voice API

```env
TWILIO_ACCOUNT_SID=AC<32文字の英数字>
TWILIO_AUTH_TOKEN=<Twilio Consoleから取得>
TWILIO_PHONE_NUMBER=+819012345678
```

##### Google Sheets API

**重要**: `credentials/credentials_oneline.txt`の内容を**1行のまま**コピーして貼り付けてください。

```env
GOOGLE_SHEETS_CREDENTIALS_JSON=<credentials/credentials_oneline.txtの内容をそのままコピー>
GOOGLE_SHEETS_SPREADSHEET_ID=<Google SheetsのスプレッドシートID>
```

**スプレッドシートIDの取得方法**:
Google SheetsのURLから取得できます：
```
https://docs.google.com/spreadsheets/d/【ここがスプレッドシートID】/edit
```

##### 管制LINE ID

井上誠司さん、近藤拓翔さんの両方に通知が送られます：

```env
CONTROL_LINE_ID=U5709d266e428a4e63d07c053e458b15f,Ud3a8a0fc1278d068a5f715d6972cc4c3
```

#### オプション環境変数（必要に応じて設定）

##### 髙木LINE ID（Procast未取得通知用）

```env
TAKAGI_LINE_ID=Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

##### Slack Webhook（エラー通知用）

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

##### Google Drive API（Procastデータ取得用）

**重要**: Google Sheets APIと同じ認証情報を使用します。

```env
GOOGLE_DRIVE_CREDENTIALS_JSON=<credentials/credentials_oneline.txtの内容をそのままコピー>
GOOGLE_DRIVE_PROCAST_FOLDER_ID=<Google DriveのフォルダID>
GOOGLE_DRIVE_PROCAST_FILE_NAME=procast_data.csv
```

##### その他のオプション設定

```env
TZ=Asia/Tokyo
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. セットアップの確認

環境変数が正しく設定されているか確認します：

```bash
python scripts/verify_setup.py
```

すべての必須環境変数が設定されていれば、以下のような出力が表示されます：

```
==================================================
Setup Verification
==================================================

[1] Required Environment Variables
  All required variables are set

[2] Optional Environment Variables
  Configured: X / Y

[3] Log Directory
  Log directory exists: C:\Users\takag\00_dev\kazuko_departure_watch\logs

==================================================
Results
==================================================
  Required Env Vars: OK
  Optional Env Vars: OK
  Log Directory: OK

Setup verification passed!
```

### 4. トラブルシューティング

#### エラー: "Missing required env vars: ..."

該当する環境変数が設定されていないか、`.env`ファイルが正しく読み込まれていません。

- `.env`ファイルがプロジェクトルートに存在するか確認
- 環境変数名のスペルミスがないか確認
- 環境変数の値が正しく設定されているか確認

#### エラー: "TWILIO_ACCOUNT_SID must match ^AC[a-z0-9]{32}$"

TwilioアカウントSIDの形式が正しくありません。`AC`で始まる34文字の文字列である必要があります。

#### エラー: "TWILIO_PHONE_NUMBER must be E.164 format"

Twilio電話番号はE.164形式（`+81`で始まる）である必要があります。

例: `+819012345678`

#### Google Sheets APIの認証エラー

1. `GOOGLE_SHEETS_CREDENTIALS_JSON`の値が1行形式であることを確認
2. サービスアカウントにスプレッドシートへのアクセス権限があることを確認
3. `GOOGLE_SHEETS_SPREADSHEET_ID`が正しいことを確認

## セキュリティに関する注意事項

- `.env`ファイルは機密情報を含むため、Gitにコミットしないでください
- `.env`ファイルは`.gitignore`に含まれています
- `credentials/`ディレクトリも`.gitignore`に含まれています
- 認証情報は安全に保管してください

## 次のステップ

環境変数の設定が完了したら、アプリケーションを起動できます：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

またはテストを実行：

```bash
python -m pytest app/tests/ -v
```
