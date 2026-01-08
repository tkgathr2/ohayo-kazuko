# おはよう和子さん - 実装状況まとめ

**作成日**: 2026年1月4日  
**ステータス**: 実装完了

---

## 📋 プロジェクト概要

**システム名**: おはよう和子さん  
**目的**: キャストの出発予定時間・起床予定時間をLINE Botで管理し、リマインド通知・電話発信・管制通知を行うシステム

---

## ✅ 実装完了機能一覧

### 1. 出発予定時間管理

#### 1.1 登録機能
- ✅ LINEメッセージで出発予定時間を登録
  - 「出発 HH:MM」形式
  - 「HH:MM」形式（出発予定時間として登録）
  - 5分単位の時刻のみ受け付け
  - 翌日の日付に自動登録

#### 1.2 報告機能
- ✅ 出発報告ボタン（Postback）で報告
  - ボタン押下時刻を出発報告時刻として記録
  - 出発判定を自動実行（OK/遅れ返/要確認）
  - Google Sheetsに記録

#### 1.3 判定ロジック
- ✅ 出発判定
  - 予定時間以前: **OK**
  - 予定時間～5分以内: **遅れ返**
  - 5分超過: **要確認**

### 2. 起床予定時間管理

#### 2.1 登録機能
- ✅ LINEメッセージで起床予定時間を登録
  - 「起床 HH:MM」形式
  - 5分単位の時刻のみ受け付け
  - 翌日の日付に自動登録
  - **ON/OFF切り替え機能**（起床予定時間登録機能の有効/無効）

#### 2.2 報告機能
- ✅ 起床報告ボタン（Postback）で報告
  - ボタン押下時刻を起床報告時刻として記録
  - 起床判定を自動実行（OK/遅れ返/要確認）
  - Google Sheetsに記録

#### 2.3 判定ロジック
- ✅ 起床判定（出発判定と同じロジック）
  - 予定時間以前: **OK**
  - 予定時間～5分以内: **遅れ返**
  - 5分超過: **要確認**

### 3. リマインド通知機能

#### 3.1 出発予定時間リマインド
- ✅ 18:00, 19:00, 20:00, 21:00, 22:00に未登録者へリマインド送信
- ✅ Procastデータ連携時は翌日出勤者のみに送信

#### 3.2 起床予定時間リマインド
- ✅ 18:00, 19:00, 20:00, 21:00, 22:00に未登録者へリマインド送信
- ✅ 起床予定時間登録機能がONのキャストのみ対象
- ✅ Procastデータ連携時は翌日出勤者のみに送信

### 4. 電話発信機能

#### 4.1 出発電話
- ✅ 電話①: 出発予定時間から5分経過後（5分間隔で5回）
- ✅ 電話②: 電話①から10分経過後（3分間隔で10回）
- ✅ 報告があった場合は自動キャンセル
- ✅ 電話発信回数をGoogle Sheetsに記録

#### 4.2 起床電話
- ✅ 電話①: 起床予定時間から5分経過後（5分間隔で5回）
- ✅ 電話②: 電話①から10分経過後（3分間隔で10回）
- ✅ 報告があった場合は自動キャンセル
- ✅ 電話発信回数をGoogle Sheetsに記録

### 5. 管制通知機能

#### 5.1 事前通知（22:30）
- ✅ 出発予定時間未登録者を管制に通知
- ✅ 起床予定時間未登録者を管制に通知
- ✅ Procastデータ連携時は翌日出勤者のみ対象

#### 5.2 緊急アラート
- ✅ 電話②完了後も報告がない場合、管制に緊急アラート送信
- ✅ 出発・起床の両方に対応
- ✅ 電話発信状況を含む詳細情報を通知

#### 5.3 通常時間未登録通知
- ✅ 24:00に通常時間を自動採用
- ✅ 通常時間未登録者を管制に通知

### 6. Procastデータ連携

#### 6.1 データ取得
- ✅ Google DriveからProcastデータ（CSV）を取得
- ✅ 18:00に自動取得
- ✅ 翌日出勤者を判定

#### 6.2 未取得通知
- ✅ 18:00, 19:00, 20:00, 21:00, 22:00にProcastデータ未取得を通知
- ✅ 20:00以降は髙木にも通知

### 7. 自動スケジューリング

#### 7.1 通常時間自動採用（24:00）
- ✅ 出発予定時間未登録の場合、通常出発予定時間を自動採用
- ✅ 起床予定時間未登録の場合、通常起床予定時間を自動採用
- ✅ 電話発信を自動スケジュール

#### 7.2 起動時スケジュール
- ✅ アプリ起動時に既存の電話をスケジュール

### 8. エラーハンドリング

#### 8.1 APIエラー処理
- ✅ LINE APIエラー処理（リトライ、指数バックオフ）
- ✅ Twilio APIエラー処理（リトライ、指数バックオフ）
- ✅ Google Sheets APIエラー処理（リトライ、指数バックオフ）

#### 8.2 Slack通知
- ✅ エラー発生時にSlackに通知（オプション）

### 9. ログ管理

#### 9.1 ログ出力
- ✅ 構造化ログ（JSON形式）
- ✅ 個人情報ハッシュ化（LINE_ID、電話番号）
- ✅ 週次ローテーション

#### 9.2 ログレベル
- ✅ DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## 🏗️ アーキテクチャ

### ディレクトリ構造

```
kazuko_departure_watch/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPIアプリケーション
│   ├── config.py                  # 設定管理
│   ├── models/                    # データモデル
│   │   ├── cast.py               # キャストモデル
│   │   └── departure.py          # 出発/起床記録モデル
│   ├── services/                  # ビジネスロジック
│   │   ├── departure_service.py   # 出発/起床判定
│   │   ├── line_service.py        # LINE API連携
│   │   ├── twilio_service.py      # Twilio API連携
│   │   ├── spreadsheet_service.py # Google Sheets連携
│   │   ├── notification_service.py # 通知サービス
│   │   ├── phone_service.py       # 電話発信サービス
│   │   └── procast_service.py     # Procastデータ取得
│   ├── handlers/                  # HTTPハンドラー
│   │   └── webhook_handler.py    # LINE Webhook処理
│   ├── schedulers/                 # スケジューラー
│   │   └── job_scheduler.py       # ジョブスケジュール
│   ├── utils/                      # ユーティリティ
│   │   ├── logger.py              # ログ設定
│   │   ├── validators.py          # バリデーション
│   │   └── error_handler.py      # エラーハンドリング
│   └── tests/                      # テスト
│       ├── test_models.py
│       ├── test_services.py
│       └── test_handlers.py
├── docs/
│   ├── DEPLOYMENT.md              # デプロイ手順
│   └── IMPLEMENTATION_SUMMARY.md  # 本ドキュメント
├── scripts/
│   ├── setup_spreadsheet.py      # スプレッドシート設定
│   └── verify_setup.py            # セットアップ確認
├── requirements.txt               # 依存パッケージ
├── README.md                      # システム概要
└── .env.example                   # 環境変数テンプレート
```

### 技術スタック

- **言語**: Python 3.11+
- **フレームワーク**: FastAPI 0.104.0+
- **スケジューラー**: APScheduler 3.10.0+
- **外部API**:
  - LINE Messaging API v2
  - Twilio Voice API
  - Google Sheets API v4
  - Google Drive API v3
  - Slack Webhook API（オプション）

---

## 📊 データモデル

### Cast（キャスト情報）

```python
class Cast(BaseModel):
    name: str                          # 氏名
    line_id: str                       # LINE ID
    phone_number: str                  # 電話番号（E.164形式）
    default_departure_time: Optional[time]  # 通常出発予定時間
    wakeup_time_registration_enabled: bool  # 起床予定時間登録ON/OFF
    default_wakeup_time: Optional[time]     # 通常起床予定時間
    wakeup_offset_minutes: int         # 起床オフセット（分）
```

### DepartureRecord（出発/起床記録）

```python
class DepartureRecord(BaseModel):
    date: str                          # 日付（YYYY-MM-DD）
    name: str                          # 氏名
    line_id: str                       # LINE ID
    
    # 出発関連
    scheduled_departure_time: Optional[time]
    actual_departure_time: Optional[datetime]
    departure_status: Optional[DepartureStatus]  # OK/遅れ返/要確認
    departure_phone_call_count: int
    
    # 起床関連
    scheduled_wakeup_time: Optional[time]
    actual_wakeup_time: Optional[datetime]
    wakeup_status: Optional[WakeupStatus]  # OK/遅れ返/要確認
    wakeup_phone_call_count: int
    
    final_result: Optional[FinalResult]  # OK/要管制
```

---

## 🔄 主要な処理フロー

### 1. 出発予定時間登録フロー

```
キャスト → LINEメッセージ「出発 08:30」
  → Webhook Handler
  → Spreadsheet Service
  → Google Sheetsに記録
  → LINE返信「出発予定時間を08:30で登録しました。」
```

### 2. 出発報告フロー

```
キャスト → 出発報告ボタン
  → Webhook Handler
  → Departure Service（判定）
  → Spreadsheet Service（記録更新）
  → Phone Service（電話キャンセル）
  → LINE返信「出発報告を受け付けました。」
```

### 3. 電話発信フロー

```
スケジューラー → 予定時間+5分
  → Phone Service
  → Twilio Service（電話発信）
  → キャストに電話
  → 報告があればキャンセル
  → 報告がなければ電話②へ
```

### 4. リマインド通知フロー

```
スケジューラー → 18:00, 19:00, 20:00, 21:00, 22:00
  → Notification Service
  → Procast Service（翌日出勤者取得）
  → 未登録者を抽出
  → LINE Service（リマインド送信）
```

---

## 🧪 テスト状況

- **テスト数**: 26個
- **結果**: すべてパス
- **カバレッジ**: 43%（外部API連携サービスはモック未対応のため低め）

---

## 📝 環境変数

### 必須環境変数

- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIアクセストークン
- `LINE_CHANNEL_SECRET`: LINE Messaging APIシークレット
- `TWILIO_ACCOUNT_SID`: TwilioアカウントSID
- `TWILIO_AUTH_TOKEN`: Twilio認証トークン
- `TWILIO_PHONE_NUMBER`: Twilio電話番号（E.164形式）
- `GOOGLE_SHEETS_CREDENTIALS_JSON`: Google Sheets認証情報（JSON）
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Google SheetsスプレッドシートID

### オプション環境変数

- `GOOGLE_DRIVE_CREDENTIALS_JSON`: Google Drive認証情報（JSON）
- `GOOGLE_DRIVE_PROCAST_FOLDER_ID`: ProcastデータフォルダID
- `GOOGLE_DRIVE_PROCAST_FILE_NAME`: Procastデータファイル名（デフォルト: procast_data.csv）
- `SLACK_WEBHOOK_URL`: Slack Webhook URL（エラー通知用）
- `CONTROL_LINE_ID`: 管制LINE ID
- `TAKAGI_LINE_ID`: 髙木LINE ID（Procast未取得通知用）
- `TZ`: タイムゾーン（デフォルト: Asia/Tokyo）
- `LOG_LEVEL`: ログレベル（デフォルト: ERROR）
- `LOG_FILE`: ログファイルパス（デフォルト: ./logs/app.log）

---

## 🚀 デプロイ準備

### 完了している項目

- ✅ `.env.example`が作成されている
- ✅ `scripts/verify_setup.py`が実装されている
- ✅ `docs/DEPLOYMENT.md`が作成されている
- ✅ すべてのドキュメントが整備されている

### デプロイ手順

1. **環境変数の設定**
   ```bash
   cp .env.example .env
   # .envファイルを編集して本番環境の値を設定
   ```

2. **セットアップ確認**
   ```bash
   python scripts/verify_setup.py
   ```

3. **アプリケーションの起動**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **LINE Webhook URLの設定**
   - LINE Developers ConsoleでWebhook URLを設定
   - Webhook URL: `https://your-domain.com/webhook/line`

---

## 📚 ドキュメント

- `README.md`: システム概要、セットアップ手順
- `docs/DEPLOYMENT.md`: デプロイ手順書
- `PROJECT_COMPLETE_REPORT.md`: プロジェクト完了報告書
- `ARCHITECTURE.md`: アーキテクチャドキュメント
- `SPECIFICATION.md`: 仕様書（文字化けあり）

---

## ✅ 実装完了チェックリスト

- [x] 出発予定時間の登録・報告
- [x] 起床予定時間の登録・報告（ON/OFF切り替え含む）
- [x] リマインド通知（Procastデータ連携含む）
- [x] 電話発信（出発・起床の両方）
- [x] 管制通知（未登録者通知、緊急アラート）
- [x] Procastデータ連携
- [x] エラーハンドリング（Slack通知含む）
- [x] ログ出力（個人情報ハッシュ化含む）
- [x] テスト（26 passed）
- [x] ドキュメント整備

---

## 🎯 次のステップ

1. **本番環境へのデプロイ**
   - 環境変数の設定
   - セットアップ確認
   - アプリケーション起動
   - LINE Webhook URL設定

2. **動作確認**
   - ヘルスチェック: `curl http://localhost:8000/health`
   - LINE Botの動作確認
   - スケジューラーの動作確認

3. **監視・メンテナンス**
   - ログファイルの確認
   - エラーの監視
   - 定期的なテスト実行

---

**実装完了日**: 2026年1月4日  
**最終更新日**: 2026年1月4日


**作成日**: 2026年1月4日  
**ステータス**: 実装完了

---

## 📋 プロジェクト概要

**システム名**: おはよう和子さん  
**目的**: キャストの出発予定時間・起床予定時間をLINE Botで管理し、リマインド通知・電話発信・管制通知を行うシステム

---

## ✅ 実装完了機能一覧

### 1. 出発予定時間管理

#### 1.1 登録機能
- ✅ LINEメッセージで出発予定時間を登録
  - 「出発 HH:MM」形式
  - 「HH:MM」形式（出発予定時間として登録）
  - 5分単位の時刻のみ受け付け
  - 翌日の日付に自動登録

#### 1.2 報告機能
- ✅ 出発報告ボタン（Postback）で報告
  - ボタン押下時刻を出発報告時刻として記録
  - 出発判定を自動実行（OK/遅れ返/要確認）
  - Google Sheetsに記録

#### 1.3 判定ロジック
- ✅ 出発判定
  - 予定時間以前: **OK**
  - 予定時間～5分以内: **遅れ返**
  - 5分超過: **要確認**

### 2. 起床予定時間管理

#### 2.1 登録機能
- ✅ LINEメッセージで起床予定時間を登録
  - 「起床 HH:MM」形式
  - 5分単位の時刻のみ受け付け
  - 翌日の日付に自動登録
  - **ON/OFF切り替え機能**（起床予定時間登録機能の有効/無効）

#### 2.2 報告機能
- ✅ 起床報告ボタン（Postback）で報告
  - ボタン押下時刻を起床報告時刻として記録
  - 起床判定を自動実行（OK/遅れ返/要確認）
  - Google Sheetsに記録

#### 2.3 判定ロジック
- ✅ 起床判定（出発判定と同じロジック）
  - 予定時間以前: **OK**
  - 予定時間～5分以内: **遅れ返**
  - 5分超過: **要確認**

### 3. リマインド通知機能

#### 3.1 出発予定時間リマインド
- ✅ 18:00, 19:00, 20:00, 21:00, 22:00に未登録者へリマインド送信
- ✅ Procastデータ連携時は翌日出勤者のみに送信

#### 3.2 起床予定時間リマインド
- ✅ 18:00, 19:00, 20:00, 21:00, 22:00に未登録者へリマインド送信
- ✅ 起床予定時間登録機能がONのキャストのみ対象
- ✅ Procastデータ連携時は翌日出勤者のみに送信

### 4. 電話発信機能

#### 4.1 出発電話
- ✅ 電話①: 出発予定時間から5分経過後（5分間隔で5回）
- ✅ 電話②: 電話①から10分経過後（3分間隔で10回）
- ✅ 報告があった場合は自動キャンセル
- ✅ 電話発信回数をGoogle Sheetsに記録

#### 4.2 起床電話
- ✅ 電話①: 起床予定時間から5分経過後（5分間隔で5回）
- ✅ 電話②: 電話①から10分経過後（3分間隔で10回）
- ✅ 報告があった場合は自動キャンセル
- ✅ 電話発信回数をGoogle Sheetsに記録

### 5. 管制通知機能

#### 5.1 事前通知（22:30）
- ✅ 出発予定時間未登録者を管制に通知
- ✅ 起床予定時間未登録者を管制に通知
- ✅ Procastデータ連携時は翌日出勤者のみ対象

#### 5.2 緊急アラート
- ✅ 電話②完了後も報告がない場合、管制に緊急アラート送信
- ✅ 出発・起床の両方に対応
- ✅ 電話発信状況を含む詳細情報を通知

#### 5.3 通常時間未登録通知
- ✅ 24:00に通常時間を自動採用
- ✅ 通常時間未登録者を管制に通知

### 6. Procastデータ連携

#### 6.1 データ取得
- ✅ Google DriveからProcastデータ（CSV）を取得
- ✅ 18:00に自動取得
- ✅ 翌日出勤者を判定

#### 6.2 未取得通知
- ✅ 18:00, 19:00, 20:00, 21:00, 22:00にProcastデータ未取得を通知
- ✅ 20:00以降は髙木にも通知

### 7. 自動スケジューリング

#### 7.1 通常時間自動採用（24:00）
- ✅ 出発予定時間未登録の場合、通常出発予定時間を自動採用
- ✅ 起床予定時間未登録の場合、通常起床予定時間を自動採用
- ✅ 電話発信を自動スケジュール

#### 7.2 起動時スケジュール
- ✅ アプリ起動時に既存の電話をスケジュール

### 8. エラーハンドリング

#### 8.1 APIエラー処理
- ✅ LINE APIエラー処理（リトライ、指数バックオフ）
- ✅ Twilio APIエラー処理（リトライ、指数バックオフ）
- ✅ Google Sheets APIエラー処理（リトライ、指数バックオフ）

#### 8.2 Slack通知
- ✅ エラー発生時にSlackに通知（オプション）

### 9. ログ管理

#### 9.1 ログ出力
- ✅ 構造化ログ（JSON形式）
- ✅ 個人情報ハッシュ化（LINE_ID、電話番号）
- ✅ 週次ローテーション

#### 9.2 ログレベル
- ✅ DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## 🏗️ アーキテクチャ

### ディレクトリ構造

```
kazuko_departure_watch/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPIアプリケーション
│   ├── config.py                  # 設定管理
│   ├── models/                    # データモデル
│   │   ├── cast.py               # キャストモデル
│   │   └── departure.py          # 出発/起床記録モデル
│   ├── services/                  # ビジネスロジック
│   │   ├── departure_service.py   # 出発/起床判定
│   │   ├── line_service.py        # LINE API連携
│   │   ├── twilio_service.py      # Twilio API連携
│   │   ├── spreadsheet_service.py # Google Sheets連携
│   │   ├── notification_service.py # 通知サービス
│   │   ├── phone_service.py       # 電話発信サービス
│   │   └── procast_service.py     # Procastデータ取得
│   ├── handlers/                  # HTTPハンドラー
│   │   └── webhook_handler.py    # LINE Webhook処理
│   ├── schedulers/                 # スケジューラー
│   │   └── job_scheduler.py       # ジョブスケジュール
│   ├── utils/                      # ユーティリティ
│   │   ├── logger.py              # ログ設定
│   │   ├── validators.py          # バリデーション
│   │   └── error_handler.py      # エラーハンドリング
│   └── tests/                      # テスト
│       ├── test_models.py
│       ├── test_services.py
│       └── test_handlers.py
├── docs/
│   ├── DEPLOYMENT.md              # デプロイ手順
│   └── IMPLEMENTATION_SUMMARY.md  # 本ドキュメント
├── scripts/
│   ├── setup_spreadsheet.py      # スプレッドシート設定
│   └── verify_setup.py            # セットアップ確認
├── requirements.txt               # 依存パッケージ
├── README.md                      # システム概要
└── .env.example                   # 環境変数テンプレート
```

### 技術スタック

- **言語**: Python 3.11+
- **フレームワーク**: FastAPI 0.104.0+
- **スケジューラー**: APScheduler 3.10.0+
- **外部API**:
  - LINE Messaging API v2
  - Twilio Voice API
  - Google Sheets API v4
  - Google Drive API v3
  - Slack Webhook API（オプション）

---

## 📊 データモデル

### Cast（キャスト情報）

```python
class Cast(BaseModel):
    name: str                          # 氏名
    line_id: str                       # LINE ID
    phone_number: str                  # 電話番号（E.164形式）
    default_departure_time: Optional[time]  # 通常出発予定時間
    wakeup_time_registration_enabled: bool  # 起床予定時間登録ON/OFF
    default_wakeup_time: Optional[time]     # 通常起床予定時間
    wakeup_offset_minutes: int         # 起床オフセット（分）
```

### DepartureRecord（出発/起床記録）

```python
class DepartureRecord(BaseModel):
    date: str                          # 日付（YYYY-MM-DD）
    name: str                          # 氏名
    line_id: str                       # LINE ID
    
    # 出発関連
    scheduled_departure_time: Optional[time]
    actual_departure_time: Optional[datetime]
    departure_status: Optional[DepartureStatus]  # OK/遅れ返/要確認
    departure_phone_call_count: int
    
    # 起床関連
    scheduled_wakeup_time: Optional[time]
    actual_wakeup_time: Optional[datetime]
    wakeup_status: Optional[WakeupStatus]  # OK/遅れ返/要確認
    wakeup_phone_call_count: int
    
    final_result: Optional[FinalResult]  # OK/要管制
```

---

## 🔄 主要な処理フロー

### 1. 出発予定時間登録フロー

```
キャスト → LINEメッセージ「出発 08:30」
  → Webhook Handler
  → Spreadsheet Service
  → Google Sheetsに記録
  → LINE返信「出発予定時間を08:30で登録しました。」
```

### 2. 出発報告フロー

```
キャスト → 出発報告ボタン
  → Webhook Handler
  → Departure Service（判定）
  → Spreadsheet Service（記録更新）
  → Phone Service（電話キャンセル）
  → LINE返信「出発報告を受け付けました。」
```

### 3. 電話発信フロー

```
スケジューラー → 予定時間+5分
  → Phone Service
  → Twilio Service（電話発信）
  → キャストに電話
  → 報告があればキャンセル
  → 報告がなければ電話②へ
```

### 4. リマインド通知フロー

```
スケジューラー → 18:00, 19:00, 20:00, 21:00, 22:00
  → Notification Service
  → Procast Service（翌日出勤者取得）
  → 未登録者を抽出
  → LINE Service（リマインド送信）
```

---

## 🧪 テスト状況

- **テスト数**: 26個
- **結果**: すべてパス
- **カバレッジ**: 43%（外部API連携サービスはモック未対応のため低め）

---

## 📝 環境変数

### 必須環境変数

- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIアクセストークン
- `LINE_CHANNEL_SECRET`: LINE Messaging APIシークレット
- `TWILIO_ACCOUNT_SID`: TwilioアカウントSID
- `TWILIO_AUTH_TOKEN`: Twilio認証トークン
- `TWILIO_PHONE_NUMBER`: Twilio電話番号（E.164形式）
- `GOOGLE_SHEETS_CREDENTIALS_JSON`: Google Sheets認証情報（JSON）
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Google SheetsスプレッドシートID

### オプション環境変数

- `GOOGLE_DRIVE_CREDENTIALS_JSON`: Google Drive認証情報（JSON）
- `GOOGLE_DRIVE_PROCAST_FOLDER_ID`: ProcastデータフォルダID
- `GOOGLE_DRIVE_PROCAST_FILE_NAME`: Procastデータファイル名（デフォルト: procast_data.csv）
- `SLACK_WEBHOOK_URL`: Slack Webhook URL（エラー通知用）
- `CONTROL_LINE_ID`: 管制LINE ID
- `TAKAGI_LINE_ID`: 髙木LINE ID（Procast未取得通知用）
- `TZ`: タイムゾーン（デフォルト: Asia/Tokyo）
- `LOG_LEVEL`: ログレベル（デフォルト: ERROR）
- `LOG_FILE`: ログファイルパス（デフォルト: ./logs/app.log）

---

## 🚀 デプロイ準備

### 完了している項目

- ✅ `.env.example`が作成されている
- ✅ `scripts/verify_setup.py`が実装されている
- ✅ `docs/DEPLOYMENT.md`が作成されている
- ✅ すべてのドキュメントが整備されている

### デプロイ手順

1. **環境変数の設定**
   ```bash
   cp .env.example .env
   # .envファイルを編集して本番環境の値を設定
   ```

2. **セットアップ確認**
   ```bash
   python scripts/verify_setup.py
   ```

3. **アプリケーションの起動**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **LINE Webhook URLの設定**
   - LINE Developers ConsoleでWebhook URLを設定
   - Webhook URL: `https://your-domain.com/webhook/line`

---

## 📚 ドキュメント

- `README.md`: システム概要、セットアップ手順
- `docs/DEPLOYMENT.md`: デプロイ手順書
- `PROJECT_COMPLETE_REPORT.md`: プロジェクト完了報告書
- `ARCHITECTURE.md`: アーキテクチャドキュメント
- `SPECIFICATION.md`: 仕様書（文字化けあり）

---

## ✅ 実装完了チェックリスト

- [x] 出発予定時間の登録・報告
- [x] 起床予定時間の登録・報告（ON/OFF切り替え含む）
- [x] リマインド通知（Procastデータ連携含む）
- [x] 電話発信（出発・起床の両方）
- [x] 管制通知（未登録者通知、緊急アラート）
- [x] Procastデータ連携
- [x] エラーハンドリング（Slack通知含む）
- [x] ログ出力（個人情報ハッシュ化含む）
- [x] テスト（26 passed）
- [x] ドキュメント整備

---

## 🎯 次のステップ

1. **本番環境へのデプロイ**
   - 環境変数の設定
   - セットアップ確認
   - アプリケーション起動
   - LINE Webhook URL設定

2. **動作確認**
   - ヘルスチェック: `curl http://localhost:8000/health`
   - LINE Botの動作確認
   - スケジューラーの動作確認

3. **監視・メンテナンス**
   - ログファイルの確認
   - エラーの監視
   - 定期的なテスト実行

---

**実装完了日**: 2026年1月4日  
**最終更新日**: 2026年1月4日


**作成日**: 2026年1月4日  
**ステータス**: 実装完了

---

## 📋 プロジェクト概要

**システム名**: おはよう和子さん  
**目的**: キャストの出発予定時間・起床予定時間をLINE Botで管理し、リマインド通知・電話発信・管制通知を行うシステム

---

## ✅ 実装完了機能一覧

### 1. 出発予定時間管理

#### 1.1 登録機能
- ✅ LINEメッセージで出発予定時間を登録
  - 「出発 HH:MM」形式
  - 「HH:MM」形式（出発予定時間として登録）
  - 5分単位の時刻のみ受け付け
  - 翌日の日付に自動登録

#### 1.2 報告機能
- ✅ 出発報告ボタン（Postback）で報告
  - ボタン押下時刻を出発報告時刻として記録
  - 出発判定を自動実行（OK/遅れ返/要確認）
  - Google Sheetsに記録

#### 1.3 判定ロジック
- ✅ 出発判定
  - 予定時間以前: **OK**
  - 予定時間～5分以内: **遅れ返**
  - 5分超過: **要確認**

### 2. 起床予定時間管理

#### 2.1 登録機能
- ✅ LINEメッセージで起床予定時間を登録
  - 「起床 HH:MM」形式
  - 5分単位の時刻のみ受け付け
  - 翌日の日付に自動登録
  - **ON/OFF切り替え機能**（起床予定時間登録機能の有効/無効）

#### 2.2 報告機能
- ✅ 起床報告ボタン（Postback）で報告
  - ボタン押下時刻を起床報告時刻として記録
  - 起床判定を自動実行（OK/遅れ返/要確認）
  - Google Sheetsに記録

#### 2.3 判定ロジック
- ✅ 起床判定（出発判定と同じロジック）
  - 予定時間以前: **OK**
  - 予定時間～5分以内: **遅れ返**
  - 5分超過: **要確認**

### 3. リマインド通知機能

#### 3.1 出発予定時間リマインド
- ✅ 18:00, 19:00, 20:00, 21:00, 22:00に未登録者へリマインド送信
- ✅ Procastデータ連携時は翌日出勤者のみに送信

#### 3.2 起床予定時間リマインド
- ✅ 18:00, 19:00, 20:00, 21:00, 22:00に未登録者へリマインド送信
- ✅ 起床予定時間登録機能がONのキャストのみ対象
- ✅ Procastデータ連携時は翌日出勤者のみに送信

### 4. 電話発信機能

#### 4.1 出発電話
- ✅ 電話①: 出発予定時間から5分経過後（5分間隔で5回）
- ✅ 電話②: 電話①から10分経過後（3分間隔で10回）
- ✅ 報告があった場合は自動キャンセル
- ✅ 電話発信回数をGoogle Sheetsに記録

#### 4.2 起床電話
- ✅ 電話①: 起床予定時間から5分経過後（5分間隔で5回）
- ✅ 電話②: 電話①から10分経過後（3分間隔で10回）
- ✅ 報告があった場合は自動キャンセル
- ✅ 電話発信回数をGoogle Sheetsに記録

### 5. 管制通知機能

#### 5.1 事前通知（22:30）
- ✅ 出発予定時間未登録者を管制に通知
- ✅ 起床予定時間未登録者を管制に通知
- ✅ Procastデータ連携時は翌日出勤者のみ対象

#### 5.2 緊急アラート
- ✅ 電話②完了後も報告がない場合、管制に緊急アラート送信
- ✅ 出発・起床の両方に対応
- ✅ 電話発信状況を含む詳細情報を通知

#### 5.3 通常時間未登録通知
- ✅ 24:00に通常時間を自動採用
- ✅ 通常時間未登録者を管制に通知

### 6. Procastデータ連携

#### 6.1 データ取得
- ✅ Google DriveからProcastデータ（CSV）を取得
- ✅ 18:00に自動取得
- ✅ 翌日出勤者を判定

#### 6.2 未取得通知
- ✅ 18:00, 19:00, 20:00, 21:00, 22:00にProcastデータ未取得を通知
- ✅ 20:00以降は髙木にも通知

### 7. 自動スケジューリング

#### 7.1 通常時間自動採用（24:00）
- ✅ 出発予定時間未登録の場合、通常出発予定時間を自動採用
- ✅ 起床予定時間未登録の場合、通常起床予定時間を自動採用
- ✅ 電話発信を自動スケジュール

#### 7.2 起動時スケジュール
- ✅ アプリ起動時に既存の電話をスケジュール

### 8. エラーハンドリング

#### 8.1 APIエラー処理
- ✅ LINE APIエラー処理（リトライ、指数バックオフ）
- ✅ Twilio APIエラー処理（リトライ、指数バックオフ）
- ✅ Google Sheets APIエラー処理（リトライ、指数バックオフ）

#### 8.2 Slack通知
- ✅ エラー発生時にSlackに通知（オプション）

### 9. ログ管理

#### 9.1 ログ出力
- ✅ 構造化ログ（JSON形式）
- ✅ 個人情報ハッシュ化（LINE_ID、電話番号）
- ✅ 週次ローテーション

#### 9.2 ログレベル
- ✅ DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## 🏗️ アーキテクチャ

### ディレクトリ構造

```
kazuko_departure_watch/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPIアプリケーション
│   ├── config.py                  # 設定管理
│   ├── models/                    # データモデル
│   │   ├── cast.py               # キャストモデル
│   │   └── departure.py          # 出発/起床記録モデル
│   ├── services/                  # ビジネスロジック
│   │   ├── departure_service.py   # 出発/起床判定
│   │   ├── line_service.py        # LINE API連携
│   │   ├── twilio_service.py      # Twilio API連携
│   │   ├── spreadsheet_service.py # Google Sheets連携
│   │   ├── notification_service.py # 通知サービス
│   │   ├── phone_service.py       # 電話発信サービス
│   │   └── procast_service.py     # Procastデータ取得
│   ├── handlers/                  # HTTPハンドラー
│   │   └── webhook_handler.py    # LINE Webhook処理
│   ├── schedulers/                 # スケジューラー
│   │   └── job_scheduler.py       # ジョブスケジュール
│   ├── utils/                      # ユーティリティ
│   │   ├── logger.py              # ログ設定
│   │   ├── validators.py          # バリデーション
│   │   └── error_handler.py      # エラーハンドリング
│   └── tests/                      # テスト
│       ├── test_models.py
│       ├── test_services.py
│       └── test_handlers.py
├── docs/
│   ├── DEPLOYMENT.md              # デプロイ手順
│   └── IMPLEMENTATION_SUMMARY.md  # 本ドキュメント
├── scripts/
│   ├── setup_spreadsheet.py      # スプレッドシート設定
│   └── verify_setup.py            # セットアップ確認
├── requirements.txt               # 依存パッケージ
├── README.md                      # システム概要
└── .env.example                   # 環境変数テンプレート
```

### 技術スタック

- **言語**: Python 3.11+
- **フレームワーク**: FastAPI 0.104.0+
- **スケジューラー**: APScheduler 3.10.0+
- **外部API**:
  - LINE Messaging API v2
  - Twilio Voice API
  - Google Sheets API v4
  - Google Drive API v3
  - Slack Webhook API（オプション）

---

## 📊 データモデル

### Cast（キャスト情報）

```python
class Cast(BaseModel):
    name: str                          # 氏名
    line_id: str                       # LINE ID
    phone_number: str                  # 電話番号（E.164形式）
    default_departure_time: Optional[time]  # 通常出発予定時間
    wakeup_time_registration_enabled: bool  # 起床予定時間登録ON/OFF
    default_wakeup_time: Optional[time]     # 通常起床予定時間
    wakeup_offset_minutes: int         # 起床オフセット（分）
```

### DepartureRecord（出発/起床記録）

```python
class DepartureRecord(BaseModel):
    date: str                          # 日付（YYYY-MM-DD）
    name: str                          # 氏名
    line_id: str                       # LINE ID
    
    # 出発関連
    scheduled_departure_time: Optional[time]
    actual_departure_time: Optional[datetime]
    departure_status: Optional[DepartureStatus]  # OK/遅れ返/要確認
    departure_phone_call_count: int
    
    # 起床関連
    scheduled_wakeup_time: Optional[time]
    actual_wakeup_time: Optional[datetime]
    wakeup_status: Optional[WakeupStatus]  # OK/遅れ返/要確認
    wakeup_phone_call_count: int
    
    final_result: Optional[FinalResult]  # OK/要管制
```

---

## 🔄 主要な処理フロー

### 1. 出発予定時間登録フロー

```
キャスト → LINEメッセージ「出発 08:30」
  → Webhook Handler
  → Spreadsheet Service
  → Google Sheetsに記録
  → LINE返信「出発予定時間を08:30で登録しました。」
```

### 2. 出発報告フロー

```
キャスト → 出発報告ボタン
  → Webhook Handler
  → Departure Service（判定）
  → Spreadsheet Service（記録更新）
  → Phone Service（電話キャンセル）
  → LINE返信「出発報告を受け付けました。」
```

### 3. 電話発信フロー

```
スケジューラー → 予定時間+5分
  → Phone Service
  → Twilio Service（電話発信）
  → キャストに電話
  → 報告があればキャンセル
  → 報告がなければ電話②へ
```

### 4. リマインド通知フロー

```
スケジューラー → 18:00, 19:00, 20:00, 21:00, 22:00
  → Notification Service
  → Procast Service（翌日出勤者取得）
  → 未登録者を抽出
  → LINE Service（リマインド送信）
```

---

## 🧪 テスト状況

- **テスト数**: 26個
- **結果**: すべてパス
- **カバレッジ**: 43%（外部API連携サービスはモック未対応のため低め）

---

## 📝 環境変数

### 必須環境変数

- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIアクセストークン
- `LINE_CHANNEL_SECRET`: LINE Messaging APIシークレット
- `TWILIO_ACCOUNT_SID`: TwilioアカウントSID
- `TWILIO_AUTH_TOKEN`: Twilio認証トークン
- `TWILIO_PHONE_NUMBER`: Twilio電話番号（E.164形式）
- `GOOGLE_SHEETS_CREDENTIALS_JSON`: Google Sheets認証情報（JSON）
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Google SheetsスプレッドシートID

### オプション環境変数

- `GOOGLE_DRIVE_CREDENTIALS_JSON`: Google Drive認証情報（JSON）
- `GOOGLE_DRIVE_PROCAST_FOLDER_ID`: ProcastデータフォルダID
- `GOOGLE_DRIVE_PROCAST_FILE_NAME`: Procastデータファイル名（デフォルト: procast_data.csv）
- `SLACK_WEBHOOK_URL`: Slack Webhook URL（エラー通知用）
- `CONTROL_LINE_ID`: 管制LINE ID
- `TAKAGI_LINE_ID`: 髙木LINE ID（Procast未取得通知用）
- `TZ`: タイムゾーン（デフォルト: Asia/Tokyo）
- `LOG_LEVEL`: ログレベル（デフォルト: ERROR）
- `LOG_FILE`: ログファイルパス（デフォルト: ./logs/app.log）

---

## 🚀 デプロイ準備

### 完了している項目

- ✅ `.env.example`が作成されている
- ✅ `scripts/verify_setup.py`が実装されている
- ✅ `docs/DEPLOYMENT.md`が作成されている
- ✅ すべてのドキュメントが整備されている

### デプロイ手順

1. **環境変数の設定**
   ```bash
   cp .env.example .env
   # .envファイルを編集して本番環境の値を設定
   ```

2. **セットアップ確認**
   ```bash
   python scripts/verify_setup.py
   ```

3. **アプリケーションの起動**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **LINE Webhook URLの設定**
   - LINE Developers ConsoleでWebhook URLを設定
   - Webhook URL: `https://your-domain.com/webhook/line`

---

## 📚 ドキュメント

- `README.md`: システム概要、セットアップ手順
- `docs/DEPLOYMENT.md`: デプロイ手順書
- `PROJECT_COMPLETE_REPORT.md`: プロジェクト完了報告書
- `ARCHITECTURE.md`: アーキテクチャドキュメント
- `SPECIFICATION.md`: 仕様書（文字化けあり）

---

## ✅ 実装完了チェックリスト

- [x] 出発予定時間の登録・報告
- [x] 起床予定時間の登録・報告（ON/OFF切り替え含む）
- [x] リマインド通知（Procastデータ連携含む）
- [x] 電話発信（出発・起床の両方）
- [x] 管制通知（未登録者通知、緊急アラート）
- [x] Procastデータ連携
- [x] エラーハンドリング（Slack通知含む）
- [x] ログ出力（個人情報ハッシュ化含む）
- [x] テスト（26 passed）
- [x] ドキュメント整備

---

## 🎯 次のステップ

1. **本番環境へのデプロイ**
   - 環境変数の設定
   - セットアップ確認
   - アプリケーション起動
   - LINE Webhook URL設定

2. **動作確認**
   - ヘルスチェック: `curl http://localhost:8000/health`
   - LINE Botの動作確認
   - スケジューラーの動作確認

3. **監視・メンテナンス**
   - ログファイルの確認
   - エラーの監視
   - 定期的なテスト実行

---

**実装完了日**: 2026年1月4日  
**最終更新日**: 2026年1月4日

