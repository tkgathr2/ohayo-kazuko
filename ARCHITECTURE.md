# 出発見守り和子さん｜アーキテクチャ設計書

## 1. システム概要

### 1.1 システム構成図

```mermaid
graph TB
    subgraph External["外部サービス"]
        LINE[LINE Messaging API]
        Twilio[Twilio Voice API]
        GoogleSheets[Google Sheets API]
    end
    
    subgraph System["出発見守り和子さんシステム"]
        FastAPI[FastAPI Server]
        Scheduler[APScheduler]
        WebhookHandler[Webhook Handler]
        NotificationService[Notification Service]
        PhoneService[Phone Service]
        SpreadsheetService[Spreadsheet Service]
    end
    
    subgraph Users["ユーザー"]
        Cast[キャスト]
        Control[管制]
    end
    
    Cast -->|LINEメッセージ| LINE
    LINE -->|Webhook| FastAPI
    FastAPI --> WebhookHandler
    WebhookHandler --> NotificationService
    WebhookHandler --> SpreadsheetService
    NotificationService --> LINE
    PhoneService --> Twilio
    Scheduler --> NotificationService
    Scheduler --> PhoneService
    Scheduler --> SpreadsheetService
    SpreadsheetService --> GoogleSheets
    Control -->|手動確認| GoogleSheets
```

### 1.2 技術スタック

| レイヤー | 技術 | バージョン |
|---------|------|-----------|
| バックエンド | FastAPI | 0.104.0+ |
| 言語 | Python | 3.11+ |
| スケジューラー | APScheduler | 3.10.0+ |
| HTTPクライアント | httpx | 最新版 |
| データ検証 | Pydantic | 2.0+ |
| ログ | Python logging | 標準ライブラリ |

---

## 2. システムアーキテクチャ

### 2.1 レイヤー構成

```
┌─────────────────────────────────────┐
│   Presentation Layer                 │
│   - LINE Webhook Handler            │
│   - Health Check Endpoint           │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   Application Layer                  │
│   - Notification Service            │
│   - Phone Service                   │
│   - Departure Logic Service         │
│   - Scheduler Service               │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   Domain Layer                       │
│   - Cast Model                      │
│   - DepartureRecord Model           │
│   - Business Logic                  │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   Infrastructure Layer               │
│   - Spreadsheet Service             │
│   - LINE API Client                 │
│   - Twilio API Client               │
│   - Error Handler                   │
│   - Logger                          │
└─────────────────────────────────────┘
```

### 2.2 ディレクトリ構造

```
kazuko_departure_watch/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPIアプリケーションエントリーポイント
│   ├── config.py               # 設定管理
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cast.py            # キャストモデル
│   │   └── departure.py       # 出発管理モデル
│   ├── services/
│   │   ├── __init__.py
│   │   ├── line_service.py    # LINE API連携
│   │   ├── twilio_service.py  # Twilio API連携
│   │   ├── spreadsheet_service.py  # Google Sheets連携
│   │   ├── notification_service.py # 通知サービス
│   │   ├── phone_service.py   # 電話サービス
│   │   └── departure_service.py   # 出発判定サービス
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── webhook_handler.py # LINE Webhook処理
│   ├── schedulers/
│   │   ├── __init__.py
│   │   └── job_scheduler.py   # スケジューラー設定
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py          # ログ設定
│   │   ├── validators.py      # バリデーション
│   │   └── error_handler.py   # エラーハンドリング
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_handlers.py
├── logs/                       # ログファイル（.gitignore）
├── .env.example               # 環境変数テンプレート
├── .gitignore
├── requirements.txt           # 依存関係
├── README.md
├── SPECIFICATION.md           # 仕様書
└── ARCHITECTURE.md            # 本ドキュメント
```

---

## 3. データフロー

### 3.1 前日出発予定時間登録フロー

```mermaid
sequenceDiagram
    participant Cast as キャスト
    participant LINE as LINE API
    participant Webhook as Webhook Handler
    participant Spreadsheet as Spreadsheet Service
    participant GoogleSheets as Google Sheets

    Cast->>LINE: 出発予定時間登録（ボタンタップ）
    LINE->>Webhook: Webhookイベント
    Webhook->>Webhook: バリデーション
    Webhook->>Spreadsheet: 出発予定時間保存
    Spreadsheet->>GoogleSheets: データ書き込み
    GoogleSheets-->>Spreadsheet: 成功
    Spreadsheet-->>Webhook: 成功
    Webhook->>LINE: 確認メッセージ送信
    LINE-->>Cast: 登録完了通知
```

### 3.2 当日出発報告フロー

```mermaid
sequenceDiagram
    participant Cast as キャスト
    participant LINE as LINE API
    participant Webhook as Webhook Handler
    participant Departure as Departure Service
    participant Spreadsheet as Spreadsheet Service
    participant GoogleSheets as Google Sheets

    Cast->>LINE: 出発報告ボタン押下
    LINE->>Webhook: Postbackイベント
    Webhook->>Webhook: 重複チェック
    Webhook->>Spreadsheet: 出発予定時間取得
    Spreadsheet->>GoogleSheets: データ読み込み
    GoogleSheets-->>Spreadsheet: データ返却
    Spreadsheet-->>Webhook: 出発予定時間
    Webhook->>Departure: 判定ロジック実行
    Departure-->>Webhook: 判定結果（OK/遅れ返）
    Webhook->>Spreadsheet: 出発時間・判定結果保存
    Spreadsheet->>GoogleSheets: データ書き込み
    GoogleSheets-->>Spreadsheet: 成功
    Spreadsheet-->>Webhook: 成功
    Webhook->>LINE: 確認メッセージ送信
    LINE-->>Cast: 報告完了通知
```

### 3.3 自動電話フロー

```mermaid
sequenceDiagram
    participant Scheduler as Scheduler
    participant Departure as Departure Service
    participant Spreadsheet as Spreadsheet Service
    participant Phone as Phone Service
    participant Twilio as Twilio API
    participant Cast as キャスト

    Scheduler->>Departure: 出発予定時間チェック
    Departure->>Spreadsheet: 未報告者リスト取得
    Spreadsheet-->>Departure: 未報告者リスト
    Departure->>Phone: 電話①開始（5分おき×5回）
    loop 5回
        Phone->>Twilio: 電話発信
        Twilio->>Cast: 電話着信
        Phone->>Phone: 5分待機
    end
    Phone->>Departure: 電話①完了
    Departure->>Phone: 電話②開始（3分おき×10回）
    loop 10回
        Phone->>Twilio: 電話発信
        Twilio->>Cast: 電話着信
        Phone->>Phone: 3分待機
    end
    Phone->>Departure: 電話②完了
    Departure->>Spreadsheet: 出発報告チェック
    alt 出発報告あり
        Departure->>Phone: 電話キャンセル
    else 出発報告なし
        Departure->>Notification: 管制通知
    end
```

### 3.4 前日リマインドフロー

```mermaid
sequenceDiagram
    participant Scheduler as Scheduler
    participant Notification as Notification Service
    participant Spreadsheet as Spreadsheet Service
    participant LINE as LINE API
    participant Cast as キャスト

    Scheduler->>Notification: リマインド時刻到達
    Notification->>Spreadsheet: 未登録者リスト取得
    Spreadsheet-->>Notification: 未登録者リスト
    loop 各未登録者
        Notification->>LINE: LINE通知送信
        LINE->>Cast: リマインドメッセージ
    end
    alt 22:30の場合
        Notification->>Notification: 管制通知生成
        Notification->>LINE: 管制へ通知
    end
```

---

## 4. 状態遷移図

### 4.1 キャストの状態遷移

```mermaid
stateDiagram-v2
    [*] --> 未登録: 前日開始
    未登録 --> 登録済み: 出発予定時間登録
    登録済み --> 待機中: 当日開始
    待機中 --> OK: 出発報告（予定時間前）
    待機中 --> 遅れ返: 出発報告（予定時間後）
    待機中 --> 要確認: 予定時間経過・未報告
    要確認 --> 電話①実行中: 電話①開始
    電話①実行中 --> 電話②実行中: 電話①完了
    電話①実行中 --> OK: 出発報告あり
    電話①実行中 --> 遅れ返: 出発報告あり（遅れ）
    電話②実行中 --> 管制対応: 電話②完了・未報告
    電話②実行中 --> OK: 出発報告あり
    電話②実行中 --> 遅れ返: 出発報告あり（遅れ）
    管制対応 --> [*]: 対応完了
    OK --> [*]: 終了
    遅れ返 --> [*]: 終了
```

### 4.2 出発レコードの状態遷移

```mermaid
stateDiagram-v2
    [*] --> 未登録: 前日開始
    未登録 --> 登録済み: 出発予定時間登録
    登録済み --> 報告済み_OK: 出発報告（予定時間前）
    登録済み --> 報告済み_遅れ返: 出発報告（予定時間後）
    登録済み --> 要確認: 予定時間経過
    要確認 --> 電話①実行中: 電話①開始
    電話①実行中 --> 電話②実行中: 電話①完了
    電話①実行中 --> 報告済み_OK: 出発報告あり（予定時間前）
    電話①実行中 --> 報告済み_遅れ返: 出発報告あり（予定時間後）
    電話②実行中 --> 管制対応: 電話②完了
    電話②実行中 --> 報告済み_OK: 出発報告あり（予定時間前）
    電話②実行中 --> 報告済み_遅れ返: 出発報告あり（予定時間後）
    管制対応 --> 最終確定: 管制が結果記入
    報告済み_OK --> [*]: 終了
    報告済み_遅れ返 --> [*]: 終了
    最終確定 --> [*]: 終了
```

---

## 5. サービス設計

### 5.1 LINE Service

**責務**:
- LINE Messaging APIとの通信
- メッセージ送信
- Webhookイベントの処理

**主要メソッド**:
- `send_message(line_id: str, message: str) -> bool`
- `send_notification(line_id: str, notification: dict) -> bool`
- `verify_signature(body: bytes, signature: str) -> bool`

### 5.2 Twilio Service

**責務**:
- Twilio Voice APIとの通信
- 電話発信
- 電話結果の記録

**主要メソッド**:
- `make_call(phone_number: str, message: str) -> dict`
- `cancel_call(call_sid: str) -> bool`

### 5.3 Spreadsheet Service

**責務**:
- Google Sheets APIとの通信
- データの読み書き
- データのバリデーション

**主要メソッド**:
- `get_casts() -> List[Cast]`
- `get_departure_records(date: date) -> List[DepartureRecord]`
- `update_departure_record(record: DepartureRecord) -> bool`
- `create_departure_record(record: DepartureRecord) -> bool`

### 5.4 Notification Service

**責務**:
- 通知の送信管理
- 未登録者・未報告者の判定
- 管制通知の生成

**主要メソッド**:
- `send_reminder_to_unregistered() -> int`
- `notify_control_unregistered() -> bool`
- `send_emergency_alert(record: DepartureRecord) -> bool`

### 5.5 Phone Service

**責務**:
- 電話発信のスケジューリング
- 電話フローの管理
- 電話結果の記録

**主要メソッド**:
- `start_phone_call_phase1(record: DepartureRecord) -> None`
- `start_phone_call_phase2(record: DepartureRecord) -> None`
- `cancel_phone_calls(record: DepartureRecord) -> None`

### 5.6 Departure Service

**責務**:
- 出発判定ロジック
- 出発時間と予定時間の比較
- 状態遷移の管理

**主要メソッド**:
- `judge_departure(actual_time: datetime, scheduled_time: datetime) -> DepartureStatus`
- `check_departure_status(record: DepartureRecord) -> DepartureStatus`
- `should_start_phone_call(record: DepartureRecord) -> bool`

---

## 6. エラーハンドリング戦略

### 6.1 エラーハンドリングフロー

```mermaid
graph TB
    Start[API呼び出し] --> Try{試行}
    Try -->|成功| Success[成功]
    Try -->|エラー| CheckType{エラー種類}
    CheckType -->|400系| LogError[ログ記録・終了]
    CheckType -->|401/403| Alert[アラート通知・終了]
    CheckType -->|429/500/503| Retry{リトライ可能?}
    Retry -->|Yes| Backoff[指数バックオフ]
    Backoff --> Try
    Retry -->|No| LogError
    CheckType -->|タイムアウト| Retry
    Success --> End[処理完了]
    LogError --> End
    Alert --> End
```

### 6.2 リトライ戦略

| API | 最大リトライ回数 | バックオフ戦略 |
|-----|----------------|---------------|
| LINE API | 3回 | 指数バックオフ（1s, 2s, 4s） |
| Twilio API | 3回 | 指数バックオフ（1s, 2s, 4s） |
| Google Sheets API | 5回 | 指数バックオフ（1s, 2s, 4s, 8s, 16s） |

---

## 7. スケジューリング設計

### 7.1 スケジューラー構成

```python
# スケジューラー設定例
scheduler = AsyncIOScheduler(timezone='Asia/Tokyo')

# 前日リマインド
scheduler.add_job(
    send_reminder_20,
    'cron',
    hour=20,
    minute=0,
    timezone='Asia/Tokyo'
)

# 当日電話（動的スケジューリング）
# 各キャストの出発予定時間に基づいて動的に生成
```

### 7.2 動的スケジューリング

- 前日24:00に、翌日の出発予定時間を読み込み
- 各キャストの出発予定時間の1分後に電話①をスケジュール
- 電話①完了後、電話②をスケジュール

---

## 8. セキュリティ設計

### 8.1 認証フロー

```mermaid
sequenceDiagram
    participant LINE as LINE API
    participant Webhook as Webhook Handler
    participant Validator as Signature Validator

    LINE->>Webhook: Webhookリクエスト（署名付き）
    Webhook->>Validator: 署名検証
    Validator->>Validator: 署名計算
    alt 署名一致
        Validator-->>Webhook: 検証成功
        Webhook->>Webhook: 処理実行
    else 署名不一致
        Validator-->>Webhook: 検証失敗
        Webhook->>Webhook: リクエスト拒否（401）
    end
```

### 8.2 データ保護

- 環境変数でAPIキーを管理
- ログには個人情報を含めない（ハッシュ化）
- HTTPS通信を必須とする

---

## 9. パフォーマンス要件

### 9.1 応答時間目標

| 処理 | 目標応答時間 |
|------|------------|
| LINE通知送信 | 3秒以内 |
| スプレッドシート読み込み | 5秒以内 |
| スプレッドシート書き込み | 5秒以内 |
| 電話発信 | 10秒以内 |

### 9.2 スループット

- 同時処理可能なLINE通知: 100件/秒
- 同時処理可能な電話発信: 10件/秒

---

## 10. 監視・ログ設計

### 10.1 ログ出力箇所

- API呼び出し（成功・失敗）
- スケジューラー実行
- エラー発生
- 重要な状態遷移

### 10.2 監視メトリクス

- API呼び出し回数
- APIエラー率
- スケジューラー実行成功率
- システム稼働率

---

## 11. デプロイ設計

### 11.1 デプロイ構成

```
本番環境
├── アプリケーションサーバー
│   ├── FastAPIアプリケーション
│   ├── APScheduler
│   └── ログファイル
└── 外部サービス
    ├── LINE Messaging API
    ├── Twilio Voice API
    └── Google Sheets API
```

### 11.2 起動シーケンス

1. 環境変数読み込み
2. ログ設定
3. データベース（スプレッドシート）接続確認
4. スケジューラー初期化
5. FastAPIサーバー起動
6. ヘルスチェック

---

**アーキテクチャ設計書バージョン**: 1.0  
**最終更新日**: 2024-01-15  
**作成者**: システム開発チーム

