# MVP版セットアップガイド

このガイドでは、おはよう和子さんプロジェクトのMVP版をセットアップする手順を説明します。

## 前提条件

- Python 3.11以上がインストールされていること
- 必要なAPIアカウントが作成されていること:
  - LINE Messaging API
  - Twilio Voice API
  - Google Cloud Platform（Sheets API有効化）

## ステップ1: Twilio認証情報の取得

### 1.1 Twilioアカウントの作成

1. [Twilio Console](https://www.twilio.com/console)にアクセス
2. アカウントを作成（無料トライアル可能）
3. ダッシュボードに移動

### 1.2 Account SIDとAuth Tokenの取得

1. Twilioダッシュボードで **Account Info** セクションを確認
2. 以下の情報をコピー:
   - **Account SID**: `AC` + 32文字の英数字（合計34文字）
   - **Auth Token**: 32文字の英数字

### 1.3 電話番号の取得

1. Twilioコンソールで **Phone Numbers** → **Buy a Number** に移動
2. 日本の電話番号を検索（+81から始まる番号）
3. 音声通話（Voice）機能を有効にした番号を購入
4. 電話番号をE.164形式でコピー（例: `+819012345678`）

**重要**:
- 無料トライアルアカウントでは、登録した電話番号にのみ電話をかけられます
- 本番環境では有料アカウントへのアップグレードが必要です

## ステップ2: .envファイルの設定

### 2.1 .envファイルの編集

プロジェクトルートの `.env` ファイルを開き、以下の値を設定してください:

```env
# Twilio Voice API
TWILIO_ACCOUNT_SID=AC〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇  # ステップ1.2で取得
TWILIO_AUTH_TOKEN=〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇〇  # ステップ1.2で取得
TWILIO_PHONE_NUMBER=+819012345678  # ステップ1.3で取得した電話番号
```

### 2.2 設定値の確認

以下の値が正しく設定されていることを確認してください:

| 項目 | 形式 | 例 |
|------|------|-----|
| TWILIO_ACCOUNT_SID | AC + 32文字 | AC1234567890abcdef1234567890abcd |
| TWILIO_AUTH_TOKEN | 32文字 | 1234567890abcdef1234567890abcdef |
| TWILIO_PHONE_NUMBER | +81で始まるE.164形式 | +819012345678 |

## ステップ3: セットアップ確認

```bash
python scripts/verify_setup.py
```

すべての項目が **OK** になることを確認してください。

**期待される出力**:
```
[1] Required Environment Variables
  All required environment variables are set

[2] Optional Environment Variables
  Not configured: 4 (MVP版では不要)

[3] Log Directory
  Log directory exists: ./logs

[4] Google Sheets Connection
  Connection successful

Results:
  Required Env Vars: OK
  Optional Env Vars: OK
  Log Directory: OK
  Google Sheets: OK
```

### エラー時の対処

#### エラー: TWILIO_ACCOUNT_SID must match ^AC[a-z0-9]{32}$

**原因**: Account SIDの形式が不正です

**対処**:
- Account SIDが `AC` で始まり、合計34文字であることを確認
- Twilioダッシュボードから正しい値をコピー

#### エラー: TWILIO_PHONE_NUMBER must be E.164 format

**原因**: 電話番号の形式が不正です

**対処**:
- 電話番号が `+81` で始まることを確認
- ハイフンやスペースを削除（例: `+81-90-1234-5678` → `+819012345678`）

#### エラー: Google Sheets Connection failed

**原因**: Google Sheets認証情報が不正、またはスプレッドシートへのアクセス権限がありません

**対処**:
1. サービスアカウントのメールアドレス（`ohayo-kazuko-sa@ohayo-kazuko-prod.iam.gserviceaccount.com`）に、スプレッドシートの編集権限を付与
2. GOOGLE_SHEETS_SPREADSHEET_IDが正しいことを確認

## ステップ4: アプリケーション起動

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**成功時の表示**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## ステップ5: 動作確認

### 5.1 ヘルスチェック

別のターミナルで以下を実行:

```bash
curl http://localhost:8000/api/ohayo-kazuko/v1/health
```

**期待される応答**:
```json
{"status":"healthy","timestamp":"2026-01-07T12:00:00+09:00"}
```

### 5.2 LINE Bot動作確認

1. LINEアプリでBotにメッセージを送信
2. 「出発 08:30」と送信 → 登録完了メッセージが返る
3. 「出発報告」ボタンをクリック → 報告完了メッセージが返る

### 5.3 MVPモード確認

以下の機能が **無効化されている** ことを確認:

- ❌ 起床予定時間の登録・報告（「この機能はMVPモードでは利用できません」というエラーメッセージが返る）
- ❌ 複数回のリマインド（20:00のみ実行）
- ❌ 電話②（電話①のみ実行）

### 5.4 ログ確認

```bash
cat logs/app.log
```

エラーがないことを確認してください。

## トラブルシューティング

### Q1: Twilioから電話がかからない

**A**: 無料トライアルアカウントの場合、Twilioコンソールで認証済み電話番号（Verified Caller IDs）に登録した番号にのみ電話をかけられます。

**対処**:
1. Twilioコンソールで **Phone Numbers** → **Verified Caller IDs** に移動
2. テスト対象の電話番号を追加
3. 認証コードを入力して確認

### Q2: ポート8000が既に使用されている

**A**: 別のアプリケーションがポート8000を使用しています。

**対処**:
```bash
# ポート番号を変更して起動
uvicorn app.main:app --host 0.0.0.0 --port 8001

# または、.envファイルで変更
API_PORT=8001
```

### Q3: Google Sheets接続エラー

**A**: サービスアカウントにスプレッドシートへのアクセス権限がありません。

**対処**:
1. Google Sheetsを開く
2. 右上の「共有」ボタンをクリック
3. サービスアカウントのメールアドレス（`ohayo-kazuko-sa@ohayo-kazuko-prod.iam.gserviceaccount.com`）を追加
4. 「編集者」権限を付与

## 次のステップ

MVP版が正常に動作したら:

1. **本番運用開始**: 実際のキャストに案内し、運用を開始
2. **1週間の安定運用**: エラーがないことを確認
3. **Phase 1へ移行**: `docs/MVP_ROADMAP.md` を参照して、段階的に機能を追加

## 参考資料

- [Twilio Console](https://www.twilio.com/console)
- [LINE Developers Console](https://developers.line.biz/console/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [MVP Roadmap](./MVP_ROADMAP.md)
- [Test Report](./TEST_REPORT.md)
