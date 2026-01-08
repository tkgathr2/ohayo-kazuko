# おはよう和子さん - 実装計画書

**作成日**: 2026年1月4日  
**ステータス**: 実装完了

---

## 1. 目的

キャストの出発予定時間・起床予定時間をLINE Botで管理し、リマインド通知・電話発信・管制通知を行うシステムを構築する。

---

## 2. 入力

### 2.1 LINEメッセージ入力
- **出発予定時間登録**: 「出発 HH:MM」形式または「HH:MM」形式
- **起床予定時間登録**: 「起床 HH:MM」形式
- **出発報告**: Postbackボタン（`action: "departure_report"`）
- **起床報告**: Postbackボタン（`action: "wakeup_report"`）
- **起床予定時間ON/OFF**: Postbackボタン（`action: "enable_wakeup_watch"` / `action: "disable_wakeup_watch"`）

### 2.2 Google Sheetsデータ
- **キャスト一覧**: 氏名、LINE_ID、電話番号、通常出発予定時間、起床予定時間設定
- **出発記録**: 日付、氏名、LINE_ID、出発予定時間、出発報告時刻、判定結果等

### 2.3 Procastデータ（Google Drive）
- CSV形式の出勤データ
- 翌日出勤者判定用

### 2.4 スケジューラー
- 18:00, 19:00, 20:00, 21:00, 22:00: リマインド通知
- 22:30: 管制通知
- 24:00: 通常時間自動採用・電話スケジュール
- 18:00: Procastデータ取得

---

## 3. 出力

### 3.1 LINEメッセージ
- リマインド通知（未登録者向け）
- 登録確認メッセージ
- 報告確認メッセージ
- 管制通知（未登録者リスト、緊急アラート）
- Procastデータ未取得通知

### 3.2 Twilio電話発信
- 出発電話①: 予定時間+5分後（5分間隔で5回）
- 出発電話②: 予定時間+15分後（3分間隔で10回）
- 起床電話①: 予定時間+5分後（5分間隔で5回）
- 起床電話②: 予定時間+15分後（3分間隔で10回）

### 3.3 Google Sheets更新
- 出発予定時間・起床予定時間の記録
- 出発報告時刻・起床報告時刻の記録
- 判定結果（OK/遅れ返/要確認）の記録
- 電話発信回数の記録
- 最終結果（OK/要管制）の記録

### 3.4 Slack通知（オプション）
- エラー通知

---

## 4. Must（必須機能）

1. **出発予定時間の登録・報告機能**
   - LINEメッセージで出発予定時間を登録
   - 出発報告ボタンで報告
   - 判定ロジック（OK/遅れ返/要確認）

2. **起床予定時間の登録・報告機能**
   - LINEメッセージで起床予定時間を登録（ON/OFF切り替え可能）
   - 起床報告ボタンで報告
   - 判定ロジック（OK/遅れ返/要確認）

3. **リマインド通知機能**
   - 18:00-22:00に未登録者へリマインド送信
   - Procastデータ連携時は翌日出勤者のみに送信

---

## 5. Won't（実装しない機能）

1. **UI管理画面**: Google Sheetsで管理
2. **過去データの編集機能**: Google Sheetsで直接編集
3. **複数日先の予定登録**: 翌日のみ対応
4. **メール通知**: LINE通知のみ
5. **SMS通知**: Twilio電話のみ

---

## 6. 成功条件

1. 出発予定時間の登録・報告が正常に動作する
2. 起床予定時間の登録・報告が正常に動作する（ON/OFF切り替え含む）
3. リマインド機能が正常に動作する（Procastデータ連携含む）
4. 電話発信機能が正常に動作する（出発・起床の両方）
5. 管制通知が正常に動作する
6. Procastデータ未取得通知が正常に動作する
7. エラーハンドリングが正常に動作する（Slack通知含む）
8. ログ出力が正常に動作する（個人情報ハッシュ化含む）
9. すべてのテストがパスする（26 passed）
10. システム名・用語が統一されている

---

## 7. エラー方針

### 7.1 APIエラー処理
- **LINE API**: 最大3回リトライ、指数バックオフ（1s, 2s, 4s）
- **Twilio API**: 最大3回リトライ、指数バックオフ（1s, 2s, 4s）
- **Google Sheets API**: 最大5回リトライ、指数バックオフ（1s, 2s, 4s, 8s, 16s）

### 7.2 エラー通知
- エラー発生時にSlackに通知（オプション）
- ログに詳細情報を記録

### 7.3 データ整合性
- Google Sheetsへの書き込み失敗時はログに記録
- 電話発信失敗時はログに記録し、次の電話を継続

---

## 8. ログ方針

### 8.1 ログレベル
- `DEBUG`: 詳細なデバッグ情報
- `INFO`: 通常の動作ログ
- `WARNING`: 警告（APIエラー等）
- `ERROR`: エラー（処理失敗等）
- `CRITICAL`: 致命的なエラー

### 8.2 ログ形式
- JSON形式（構造化ログ）
- 個人情報ハッシュ化（LINE_ID、電話番号）

### 8.3 ログファイル
- パス: `./logs/app.log`
- 週次ローテーション

### 8.4 ログ出力内容
- API呼び出し（成功・失敗）
- スケジューラー実行
- エラー詳細
- ビジネスロジックの実行状況

---

## 9. 技術仕様

### 9.1 技術スタック
- **言語**: Python 3.11+
- **フレームワーク**: FastAPI 0.104.0+
- **スケジューラー**: APScheduler 3.10.0+
- **外部API**:
  - LINE Messaging API v2
  - Twilio Voice API
  - Google Sheets API v4
  - Google Drive API v3
  - Slack Webhook API（オプション）

### 9.2 データモデル

#### Cast（キャスト情報）
- `name`: 氏名
- `line_id`: LINE ID
- `phone_number`: 電話番号（E.164形式）
- `default_departure_time`: 通常出発予定時間
- `wakeup_time_registration_enabled`: 起床予定時間登録ON/OFF
- `default_wakeup_time`: 通常起床予定時間
- `wakeup_offset_minutes`: 起床オフセット（分）

#### DepartureRecord（出発/起床記録）
- `date`: 日付（YYYY-MM-DD）
- `name`: 氏名
- `line_id`: LINE ID
- `scheduled_departure_time`: 出発予定時間
- `actual_departure_time`: 出発報告時刻
- `departure_status`: 出発判定（OK/遅れ返/要確認）
- `departure_phone_call_count`: 出発電話発信回数
- `scheduled_wakeup_time`: 起床予定時間
- `actual_wakeup_time`: 起床報告時刻
- `wakeup_status`: 起床判定（OK/遅れ返/要確認）
- `wakeup_phone_call_count`: 起床電話発信回数
- `final_result`: 最終結果（OK/要管制）

### 9.3 判定ロジック

#### 出発判定
- 予定時間以前: **OK**
- 予定時間～5分以内: **遅れ返**
- 5分超過: **要確認**

#### 起床判定
- 出発判定と同じロジック

### 9.4 電話発信タイミング

#### 出発電話
- 電話①: 出発予定時間から5分経過後（5分間隔で5回）
- 電話②: 電話①から10分経過後（3分間隔で10回）

#### 起床電話
- 電話①: 起床予定時間から5分経過後（5分間隔で5回）
- 電話②: 電話①から10分経過後（3分間隔で10回）

---

## 10. スケジュール

### 10.1 リマインド通知
- **時刻**: 18:00, 19:00, 20:00, 21:00, 22:00
- **対象**: 未登録者（Procast連携時は翌日出勤者のみ）
- **内容**: 出発予定時間・起床予定時間の登録依頼

### 10.2 管制通知
- **時刻**: 22:30
- **対象**: 未登録者リスト
- **内容**: 出発予定時間・起床予定時間未登録者を管制に通知

### 10.3 通常時間自動採用
- **時刻**: 24:00（0:00）
- **処理**: 通常出発予定時間・通常起床予定時間を自動採用
- **電話スケジュール**: 自動スケジュール

### 10.4 Procastデータ取得
- **時刻**: 18:00
- **処理**: Google DriveからProcastデータを取得

### 10.5 Procastデータ未取得通知
- **時刻**: 18:00, 19:00, 20:00, 21:00, 22:00
- **条件**: Procastデータが取得されていない場合
- **通知先**: 管制（20:00以降は髙木にも通知）

---

## 11. 環境変数

### 11.1 必須環境変数
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIアクセストークン
- `LINE_CHANNEL_SECRET`: LINE Messaging APIシークレット
- `TWILIO_ACCOUNT_SID`: TwilioアカウントSID
- `TWILIO_AUTH_TOKEN`: Twilio認証トークン
- `TWILIO_PHONE_NUMBER`: Twilio電話番号（E.164形式）
- `GOOGLE_SHEETS_CREDENTIALS_JSON`: Google Sheets認証情報（JSON）
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Google SheetsスプレッドシートID

### 11.2 オプション環境変数
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

## 12. 実装完了確認

### 12.1 機能実装
- [x] 出発予定時間の登録・報告
- [x] 起床予定時間の登録・報告（ON/OFF切り替え含む）
- [x] リマインド通知（Procastデータ連携含む）
- [x] 電話発信（出発・起床の両方）
- [x] 管制通知（未登録者通知、緊急アラート）
- [x] Procastデータ連携
- [x] エラーハンドリング（Slack通知含む）
- [x] ログ出力（個人情報ハッシュ化含む）

### 12.2 テスト
- [x] テスト数: 26個
- [x] 結果: すべてパス
- [x] カバレッジ: 43%（外部API連携サービスはモック未対応のため低め）

### 12.3 ドキュメント
- [x] README.md
- [x] docs/DEPLOYMENT.md
- [x] docs/IMPLEMENTATION_SUMMARY.md
- [x] docs/plan.md（本ドキュメント）

---

**作成日**: 2026年1月4日  
**最終更新日**: 2026年1月4日  
**ステータス**: 実装完了


**作成日**: 2026年1月4日  
**ステータス**: 実装完了

---

## 1. 目的

キャストの出発予定時間・起床予定時間をLINE Botで管理し、リマインド通知・電話発信・管制通知を行うシステムを構築する。

---

## 2. 入力

### 2.1 LINEメッセージ入力
- **出発予定時間登録**: 「出発 HH:MM」形式または「HH:MM」形式
- **起床予定時間登録**: 「起床 HH:MM」形式
- **出発報告**: Postbackボタン（`action: "departure_report"`）
- **起床報告**: Postbackボタン（`action: "wakeup_report"`）
- **起床予定時間ON/OFF**: Postbackボタン（`action: "enable_wakeup_watch"` / `action: "disable_wakeup_watch"`）

### 2.2 Google Sheetsデータ
- **キャスト一覧**: 氏名、LINE_ID、電話番号、通常出発予定時間、起床予定時間設定
- **出発記録**: 日付、氏名、LINE_ID、出発予定時間、出発報告時刻、判定結果等

### 2.3 Procastデータ（Google Drive）
- CSV形式の出勤データ
- 翌日出勤者判定用

### 2.4 スケジューラー
- 18:00, 19:00, 20:00, 21:00, 22:00: リマインド通知
- 22:30: 管制通知
- 24:00: 通常時間自動採用・電話スケジュール
- 18:00: Procastデータ取得

---

## 3. 出力

### 3.1 LINEメッセージ
- リマインド通知（未登録者向け）
- 登録確認メッセージ
- 報告確認メッセージ
- 管制通知（未登録者リスト、緊急アラート）
- Procastデータ未取得通知

### 3.2 Twilio電話発信
- 出発電話①: 予定時間+5分後（5分間隔で5回）
- 出発電話②: 予定時間+15分後（3分間隔で10回）
- 起床電話①: 予定時間+5分後（5分間隔で5回）
- 起床電話②: 予定時間+15分後（3分間隔で10回）

### 3.3 Google Sheets更新
- 出発予定時間・起床予定時間の記録
- 出発報告時刻・起床報告時刻の記録
- 判定結果（OK/遅れ返/要確認）の記録
- 電話発信回数の記録
- 最終結果（OK/要管制）の記録

### 3.4 Slack通知（オプション）
- エラー通知

---

## 4. Must（必須機能）

1. **出発予定時間の登録・報告機能**
   - LINEメッセージで出発予定時間を登録
   - 出発報告ボタンで報告
   - 判定ロジック（OK/遅れ返/要確認）

2. **起床予定時間の登録・報告機能**
   - LINEメッセージで起床予定時間を登録（ON/OFF切り替え可能）
   - 起床報告ボタンで報告
   - 判定ロジック（OK/遅れ返/要確認）

3. **リマインド通知機能**
   - 18:00-22:00に未登録者へリマインド送信
   - Procastデータ連携時は翌日出勤者のみに送信

---

## 5. Won't（実装しない機能）

1. **UI管理画面**: Google Sheetsで管理
2. **過去データの編集機能**: Google Sheetsで直接編集
3. **複数日先の予定登録**: 翌日のみ対応
4. **メール通知**: LINE通知のみ
5. **SMS通知**: Twilio電話のみ

---

## 6. 成功条件

1. 出発予定時間の登録・報告が正常に動作する
2. 起床予定時間の登録・報告が正常に動作する（ON/OFF切り替え含む）
3. リマインド機能が正常に動作する（Procastデータ連携含む）
4. 電話発信機能が正常に動作する（出発・起床の両方）
5. 管制通知が正常に動作する
6. Procastデータ未取得通知が正常に動作する
7. エラーハンドリングが正常に動作する（Slack通知含む）
8. ログ出力が正常に動作する（個人情報ハッシュ化含む）
9. すべてのテストがパスする（26 passed）
10. システム名・用語が統一されている

---

## 7. エラー方針

### 7.1 APIエラー処理
- **LINE API**: 最大3回リトライ、指数バックオフ（1s, 2s, 4s）
- **Twilio API**: 最大3回リトライ、指数バックオフ（1s, 2s, 4s）
- **Google Sheets API**: 最大5回リトライ、指数バックオフ（1s, 2s, 4s, 8s, 16s）

### 7.2 エラー通知
- エラー発生時にSlackに通知（オプション）
- ログに詳細情報を記録

### 7.3 データ整合性
- Google Sheetsへの書き込み失敗時はログに記録
- 電話発信失敗時はログに記録し、次の電話を継続

---

## 8. ログ方針

### 8.1 ログレベル
- `DEBUG`: 詳細なデバッグ情報
- `INFO`: 通常の動作ログ
- `WARNING`: 警告（APIエラー等）
- `ERROR`: エラー（処理失敗等）
- `CRITICAL`: 致命的なエラー

### 8.2 ログ形式
- JSON形式（構造化ログ）
- 個人情報ハッシュ化（LINE_ID、電話番号）

### 8.3 ログファイル
- パス: `./logs/app.log`
- 週次ローテーション

### 8.4 ログ出力内容
- API呼び出し（成功・失敗）
- スケジューラー実行
- エラー詳細
- ビジネスロジックの実行状況

---

## 9. 技術仕様

### 9.1 技術スタック
- **言語**: Python 3.11+
- **フレームワーク**: FastAPI 0.104.0+
- **スケジューラー**: APScheduler 3.10.0+
- **外部API**:
  - LINE Messaging API v2
  - Twilio Voice API
  - Google Sheets API v4
  - Google Drive API v3
  - Slack Webhook API（オプション）

### 9.2 データモデル

#### Cast（キャスト情報）
- `name`: 氏名
- `line_id`: LINE ID
- `phone_number`: 電話番号（E.164形式）
- `default_departure_time`: 通常出発予定時間
- `wakeup_time_registration_enabled`: 起床予定時間登録ON/OFF
- `default_wakeup_time`: 通常起床予定時間
- `wakeup_offset_minutes`: 起床オフセット（分）

#### DepartureRecord（出発/起床記録）
- `date`: 日付（YYYY-MM-DD）
- `name`: 氏名
- `line_id`: LINE ID
- `scheduled_departure_time`: 出発予定時間
- `actual_departure_time`: 出発報告時刻
- `departure_status`: 出発判定（OK/遅れ返/要確認）
- `departure_phone_call_count`: 出発電話発信回数
- `scheduled_wakeup_time`: 起床予定時間
- `actual_wakeup_time`: 起床報告時刻
- `wakeup_status`: 起床判定（OK/遅れ返/要確認）
- `wakeup_phone_call_count`: 起床電話発信回数
- `final_result`: 最終結果（OK/要管制）

### 9.3 判定ロジック

#### 出発判定
- 予定時間以前: **OK**
- 予定時間～5分以内: **遅れ返**
- 5分超過: **要確認**

#### 起床判定
- 出発判定と同じロジック

### 9.4 電話発信タイミング

#### 出発電話
- 電話①: 出発予定時間から5分経過後（5分間隔で5回）
- 電話②: 電話①から10分経過後（3分間隔で10回）

#### 起床電話
- 電話①: 起床予定時間から5分経過後（5分間隔で5回）
- 電話②: 電話①から10分経過後（3分間隔で10回）

---

## 10. スケジュール

### 10.1 リマインド通知
- **時刻**: 18:00, 19:00, 20:00, 21:00, 22:00
- **対象**: 未登録者（Procast連携時は翌日出勤者のみ）
- **内容**: 出発予定時間・起床予定時間の登録依頼

### 10.2 管制通知
- **時刻**: 22:30
- **対象**: 未登録者リスト
- **内容**: 出発予定時間・起床予定時間未登録者を管制に通知

### 10.3 通常時間自動採用
- **時刻**: 24:00（0:00）
- **処理**: 通常出発予定時間・通常起床予定時間を自動採用
- **電話スケジュール**: 自動スケジュール

### 10.4 Procastデータ取得
- **時刻**: 18:00
- **処理**: Google DriveからProcastデータを取得

### 10.5 Procastデータ未取得通知
- **時刻**: 18:00, 19:00, 20:00, 21:00, 22:00
- **条件**: Procastデータが取得されていない場合
- **通知先**: 管制（20:00以降は髙木にも通知）

---

## 11. 環境変数

### 11.1 必須環境変数
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIアクセストークン
- `LINE_CHANNEL_SECRET`: LINE Messaging APIシークレット
- `TWILIO_ACCOUNT_SID`: TwilioアカウントSID
- `TWILIO_AUTH_TOKEN`: Twilio認証トークン
- `TWILIO_PHONE_NUMBER`: Twilio電話番号（E.164形式）
- `GOOGLE_SHEETS_CREDENTIALS_JSON`: Google Sheets認証情報（JSON）
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Google SheetsスプレッドシートID

### 11.2 オプション環境変数
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

## 12. 実装完了確認

### 12.1 機能実装
- [x] 出発予定時間の登録・報告
- [x] 起床予定時間の登録・報告（ON/OFF切り替え含む）
- [x] リマインド通知（Procastデータ連携含む）
- [x] 電話発信（出発・起床の両方）
- [x] 管制通知（未登録者通知、緊急アラート）
- [x] Procastデータ連携
- [x] エラーハンドリング（Slack通知含む）
- [x] ログ出力（個人情報ハッシュ化含む）

### 12.2 テスト
- [x] テスト数: 26個
- [x] 結果: すべてパス
- [x] カバレッジ: 43%（外部API連携サービスはモック未対応のため低め）

### 12.3 ドキュメント
- [x] README.md
- [x] docs/DEPLOYMENT.md
- [x] docs/IMPLEMENTATION_SUMMARY.md
- [x] docs/plan.md（本ドキュメント）

---

**作成日**: 2026年1月4日  
**最終更新日**: 2026年1月4日  
**ステータス**: 実装完了


**作成日**: 2026年1月4日  
**ステータス**: 実装完了

---

## 1. 目的

キャストの出発予定時間・起床予定時間をLINE Botで管理し、リマインド通知・電話発信・管制通知を行うシステムを構築する。

---

## 2. 入力

### 2.1 LINEメッセージ入力
- **出発予定時間登録**: 「出発 HH:MM」形式または「HH:MM」形式
- **起床予定時間登録**: 「起床 HH:MM」形式
- **出発報告**: Postbackボタン（`action: "departure_report"`）
- **起床報告**: Postbackボタン（`action: "wakeup_report"`）
- **起床予定時間ON/OFF**: Postbackボタン（`action: "enable_wakeup_watch"` / `action: "disable_wakeup_watch"`）

### 2.2 Google Sheetsデータ
- **キャスト一覧**: 氏名、LINE_ID、電話番号、通常出発予定時間、起床予定時間設定
- **出発記録**: 日付、氏名、LINE_ID、出発予定時間、出発報告時刻、判定結果等

### 2.3 Procastデータ（Google Drive）
- CSV形式の出勤データ
- 翌日出勤者判定用

### 2.4 スケジューラー
- 18:00, 19:00, 20:00, 21:00, 22:00: リマインド通知
- 22:30: 管制通知
- 24:00: 通常時間自動採用・電話スケジュール
- 18:00: Procastデータ取得

---

## 3. 出力

### 3.1 LINEメッセージ
- リマインド通知（未登録者向け）
- 登録確認メッセージ
- 報告確認メッセージ
- 管制通知（未登録者リスト、緊急アラート）
- Procastデータ未取得通知

### 3.2 Twilio電話発信
- 出発電話①: 予定時間+5分後（5分間隔で5回）
- 出発電話②: 予定時間+15分後（3分間隔で10回）
- 起床電話①: 予定時間+5分後（5分間隔で5回）
- 起床電話②: 予定時間+15分後（3分間隔で10回）

### 3.3 Google Sheets更新
- 出発予定時間・起床予定時間の記録
- 出発報告時刻・起床報告時刻の記録
- 判定結果（OK/遅れ返/要確認）の記録
- 電話発信回数の記録
- 最終結果（OK/要管制）の記録

### 3.4 Slack通知（オプション）
- エラー通知

---

## 4. Must（必須機能）

1. **出発予定時間の登録・報告機能**
   - LINEメッセージで出発予定時間を登録
   - 出発報告ボタンで報告
   - 判定ロジック（OK/遅れ返/要確認）

2. **起床予定時間の登録・報告機能**
   - LINEメッセージで起床予定時間を登録（ON/OFF切り替え可能）
   - 起床報告ボタンで報告
   - 判定ロジック（OK/遅れ返/要確認）

3. **リマインド通知機能**
   - 18:00-22:00に未登録者へリマインド送信
   - Procastデータ連携時は翌日出勤者のみに送信

---

## 5. Won't（実装しない機能）

1. **UI管理画面**: Google Sheetsで管理
2. **過去データの編集機能**: Google Sheetsで直接編集
3. **複数日先の予定登録**: 翌日のみ対応
4. **メール通知**: LINE通知のみ
5. **SMS通知**: Twilio電話のみ

---

## 6. 成功条件

1. 出発予定時間の登録・報告が正常に動作する
2. 起床予定時間の登録・報告が正常に動作する（ON/OFF切り替え含む）
3. リマインド機能が正常に動作する（Procastデータ連携含む）
4. 電話発信機能が正常に動作する（出発・起床の両方）
5. 管制通知が正常に動作する
6. Procastデータ未取得通知が正常に動作する
7. エラーハンドリングが正常に動作する（Slack通知含む）
8. ログ出力が正常に動作する（個人情報ハッシュ化含む）
9. すべてのテストがパスする（26 passed）
10. システム名・用語が統一されている

---

## 7. エラー方針

### 7.1 APIエラー処理
- **LINE API**: 最大3回リトライ、指数バックオフ（1s, 2s, 4s）
- **Twilio API**: 最大3回リトライ、指数バックオフ（1s, 2s, 4s）
- **Google Sheets API**: 最大5回リトライ、指数バックオフ（1s, 2s, 4s, 8s, 16s）

### 7.2 エラー通知
- エラー発生時にSlackに通知（オプション）
- ログに詳細情報を記録

### 7.3 データ整合性
- Google Sheetsへの書き込み失敗時はログに記録
- 電話発信失敗時はログに記録し、次の電話を継続

---

## 8. ログ方針

### 8.1 ログレベル
- `DEBUG`: 詳細なデバッグ情報
- `INFO`: 通常の動作ログ
- `WARNING`: 警告（APIエラー等）
- `ERROR`: エラー（処理失敗等）
- `CRITICAL`: 致命的なエラー

### 8.2 ログ形式
- JSON形式（構造化ログ）
- 個人情報ハッシュ化（LINE_ID、電話番号）

### 8.3 ログファイル
- パス: `./logs/app.log`
- 週次ローテーション

### 8.4 ログ出力内容
- API呼び出し（成功・失敗）
- スケジューラー実行
- エラー詳細
- ビジネスロジックの実行状況

---

## 9. 技術仕様

### 9.1 技術スタック
- **言語**: Python 3.11+
- **フレームワーク**: FastAPI 0.104.0+
- **スケジューラー**: APScheduler 3.10.0+
- **外部API**:
  - LINE Messaging API v2
  - Twilio Voice API
  - Google Sheets API v4
  - Google Drive API v3
  - Slack Webhook API（オプション）

### 9.2 データモデル

#### Cast（キャスト情報）
- `name`: 氏名
- `line_id`: LINE ID
- `phone_number`: 電話番号（E.164形式）
- `default_departure_time`: 通常出発予定時間
- `wakeup_time_registration_enabled`: 起床予定時間登録ON/OFF
- `default_wakeup_time`: 通常起床予定時間
- `wakeup_offset_minutes`: 起床オフセット（分）

#### DepartureRecord（出発/起床記録）
- `date`: 日付（YYYY-MM-DD）
- `name`: 氏名
- `line_id`: LINE ID
- `scheduled_departure_time`: 出発予定時間
- `actual_departure_time`: 出発報告時刻
- `departure_status`: 出発判定（OK/遅れ返/要確認）
- `departure_phone_call_count`: 出発電話発信回数
- `scheduled_wakeup_time`: 起床予定時間
- `actual_wakeup_time`: 起床報告時刻
- `wakeup_status`: 起床判定（OK/遅れ返/要確認）
- `wakeup_phone_call_count`: 起床電話発信回数
- `final_result`: 最終結果（OK/要管制）

### 9.3 判定ロジック

#### 出発判定
- 予定時間以前: **OK**
- 予定時間～5分以内: **遅れ返**
- 5分超過: **要確認**

#### 起床判定
- 出発判定と同じロジック

### 9.4 電話発信タイミング

#### 出発電話
- 電話①: 出発予定時間から5分経過後（5分間隔で5回）
- 電話②: 電話①から10分経過後（3分間隔で10回）

#### 起床電話
- 電話①: 起床予定時間から5分経過後（5分間隔で5回）
- 電話②: 電話①から10分経過後（3分間隔で10回）

---

## 10. スケジュール

### 10.1 リマインド通知
- **時刻**: 18:00, 19:00, 20:00, 21:00, 22:00
- **対象**: 未登録者（Procast連携時は翌日出勤者のみ）
- **内容**: 出発予定時間・起床予定時間の登録依頼

### 10.2 管制通知
- **時刻**: 22:30
- **対象**: 未登録者リスト
- **内容**: 出発予定時間・起床予定時間未登録者を管制に通知

### 10.3 通常時間自動採用
- **時刻**: 24:00（0:00）
- **処理**: 通常出発予定時間・通常起床予定時間を自動採用
- **電話スケジュール**: 自動スケジュール

### 10.4 Procastデータ取得
- **時刻**: 18:00
- **処理**: Google DriveからProcastデータを取得

### 10.5 Procastデータ未取得通知
- **時刻**: 18:00, 19:00, 20:00, 21:00, 22:00
- **条件**: Procastデータが取得されていない場合
- **通知先**: 管制（20:00以降は髙木にも通知）

---

## 11. 環境変数

### 11.1 必須環境変数
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIアクセストークン
- `LINE_CHANNEL_SECRET`: LINE Messaging APIシークレット
- `TWILIO_ACCOUNT_SID`: TwilioアカウントSID
- `TWILIO_AUTH_TOKEN`: Twilio認証トークン
- `TWILIO_PHONE_NUMBER`: Twilio電話番号（E.164形式）
- `GOOGLE_SHEETS_CREDENTIALS_JSON`: Google Sheets認証情報（JSON）
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Google SheetsスプレッドシートID

### 11.2 オプション環境変数
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

## 12. 実装完了確認

### 12.1 機能実装
- [x] 出発予定時間の登録・報告
- [x] 起床予定時間の登録・報告（ON/OFF切り替え含む）
- [x] リマインド通知（Procastデータ連携含む）
- [x] 電話発信（出発・起床の両方）
- [x] 管制通知（未登録者通知、緊急アラート）
- [x] Procastデータ連携
- [x] エラーハンドリング（Slack通知含む）
- [x] ログ出力（個人情報ハッシュ化含む）

### 12.2 テスト
- [x] テスト数: 26個
- [x] 結果: すべてパス
- [x] カバレッジ: 43%（外部API連携サービスはモック未対応のため低め）

### 12.3 ドキュメント
- [x] README.md
- [x] docs/DEPLOYMENT.md
- [x] docs/IMPLEMENTATION_SUMMARY.md
- [x] docs/plan.md（本ドキュメント）

---

**作成日**: 2026年1月4日  
**最終更新日**: 2026年1月4日  
**ステータス**: 実装完了

