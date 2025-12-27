# 出発見守り和子さん - コーデックス実装プロンプト

## プロジェクト概要

出勤前の確認を自動化するシステム「出発見守り和子さん」を実装してください。

**基本方針**:
- 判定は出発報告ボタンを押した時刻のみを使用
- 電話の着信・応答・留守電は判定に使わない
- 管制は最終段階のみ介入

## 技術スタック

- **バックエンド**: FastAPI 0.104.0+
- **言語**: Python 3.11+
- **スケジューラー**: APScheduler 3.10.0+
- **HTTPクライアント**: httpx
- **データ検証**: Pydantic 2.0+
- **外部API**: LINE Messaging API v2, Twilio Voice API, Google Sheets API v4

## ディレクトリ構造

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
└── README.md
```

## データモデル

### Cast（キャスト）

```python
from datetime import time
from typing import Optional
from pydantic import BaseModel, Field, validator

class Cast(BaseModel):
    name: str = Field(..., max_length=100, description="氏名")
    line_id: str = Field(..., max_length=100, regex=r'^[a-zA-Z0-9_]+$', description="LINE_ID")
    phone_number: str = Field(..., regex=r'^\+[1-9]\d{1,14}$', description="電話番号（E.164形式）")
    default_departure_time: Optional[time] = Field(None, description="通常出発予定時間（HH:MM、5分単位）")
    department: Optional[str] = Field(None, max_length=100, description="所属")
    notes: Optional[str] = Field(None, max_length=500, description="備考")
```

### DepartureRecord（出発管理）

```python
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class DepartureStatus(str, Enum):
    OK = "OK"
    DELAYED = "遅れ返"
    NEED_CHECK = "要確認"
    CONTROL = "管制対応"

class FinalResult(str, Enum):
    ATTENDANCE_OK = "出勤OK"
    LATE = "遅刻"
    FILLED = "穴埋め"
    UNDETERMINED = "未確定"

class DepartureRecord(BaseModel):
    date: date = Field(..., description="日付（YYYY-MM-DD）")
    name: str = Field(..., max_length=100, description="氏名")
    line_id: str = Field(..., max_length=100, description="LINE_ID")
    scheduled_departure_time: Optional[datetime] = Field(None, description="出発予定時間（JST）")
    actual_departure_time: Optional[datetime] = Field(None, description="出発時間（JST、ミリ秒まで）")
    departure_status: Optional[DepartureStatus] = Field(None, description="出発判定")
    phone_call_count: int = Field(0, ge=0, le=2, description="出発電話回数（0/1/2）")
    final_result: Optional[FinalResult] = Field(None, description="最終結果")
    control_notes: Optional[str] = Field(None, max_length=1000, description="管制メモ")
```

## 環境変数

### 必須環境変数

```python
LINE_CHANNEL_ACCESS_TOKEN: str  # LINE Messaging APIのアクセストークン
LINE_CHANNEL_SECRET: str        # LINE Messaging APIのシークレット
TWILIO_ACCOUNT_SID: str         # TwilioアカウントSID（正規表現: ^AC[a-z0-9]{32}$）
TWILIO_AUTH_TOKEN: str          # Twilio認証トークン
TWILIO_PHONE_NUMBER: str        # Twilio発信元電話番号（E.164形式）
GOOGLE_SHEETS_CREDENTIALS_JSON: str  # Google Sheets API認証情報（JSON文字列）
GOOGLE_SHEETS_SPREADSHEET_ID: str    # スプレッドシートID
TZ: str = "Asia/Tokyo"          # タイムゾーン
```

### オプション環境変数

```python
LOG_LEVEL: str = "INFO"
LOG_FILE: str = "./logs/app.log"
API_HOST: str = "0.0.0.0"
API_PORT: int = 8000
```

## 主要機能要件

### 1. 前日出発予定時間登録

- LINEで時→分の2タップで登録（5分単位のみ）
- データ形式: 時（0-23）、分（0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55）
- 日付は登録日の翌日（システムが自動判定）
- Googleスプレッドシート「出発見守り_当日管理」に保存

### 2. 前日リマインド（スケジューラー）

| 時刻 | 処理 |
|------|------|
| 20:00 JST | 未登録者にLINE通知 |
| 21:00 JST | 未登録者にLINE通知 |
| 22:00 JST | 未登録者にLINE通知 |
| 22:30 JST | 管制へ未登録者通知（人数＋氏名） |
| 23:00 JST | 未登録者に最終LINE通知 |
| 24:00 JST | 通常出発予定時間を自動採用（無ければ管制通知） |

### 3. 当日出発報告

- LINEの「出発報告」ボタン（Postback）を押す
- 重複押下は「既に出発報告済みです」と表示、処理スキップ
- 判定ロジック:
  - `出発時間 <= 出発予定時間` → "OK"（何もしない）
  - `出発時間 > 出発予定時間` → "遅れ返"（ログのみ）
  - `出発予定時間までに未報告` → "要確認"（自動電話へ）

**重要**: 時刻比較は秒単位（ミリ秒は切り捨て）

### 4. 自動電話（出発予定時間の1分後から開始）

- **電話①**: 5分おき × 5回（約25分）
- **電話②**: 3分おき × 10回（約30分）
- **合計**: 約45分
- 音声メッセージ: 「おはようございます。出発見守り和子さんです。本日の出発報告をお願いします。LINEの出発報告ボタンを押してください。」
- 電話中に出発報告があった場合、残りの電話は即座にキャンセル
- **重要**: 電話の結果（着信・応答・留守電）は判定に使わない

### 5. 管制通知

- **条件**: 電話①②完走後も出発報告なし
- **タイミング**: 電話②の最後の電話が終了した時点
- **内容**: 氏名、出発予定時間、現在時刻、電話①②の完了状況

## 判定ロジック（Python実装）

```python
from datetime import datetime
from typing import Optional

def judge_departure(actual_time: Optional[datetime], scheduled_time: datetime, current_time: datetime) -> Optional[str]:
    """
    出発判定ロジック
    
    Args:
        actual_time: 出発報告ボタン押下時刻（JST、Noneの場合は未報告）
        scheduled_time: 出発予定時間（JST）
        current_time: 現在時刻（JST）
    
    Returns:
        "OK" / "遅れ返" / "要確認" / None（まだ判定できない）
    """
    if actual_time is None:
        # 出発報告が無い
        if current_time > scheduled_time:
            return "要確認"
        else:
            return None  # まだ判定できない
    
    # 時刻比較（秒単位、ミリ秒は切り捨て）
    actual_seconds = actual_time.replace(microsecond=0)
    scheduled_seconds = scheduled_time.replace(microsecond=0)
    
    if actual_seconds <= scheduled_seconds:
        return "OK"
    else:
        return "遅れ返"
```

## Googleスプレッドシート構造

### シート①：キャスト一覧

| 列名 | データ型 | 必須 | 形式・制約 |
|------|----------|------|------------|
| 氏名 | string | Yes | 最大100文字 |
| LINE_ID | string | Yes | 最大100文字、英数字とアンダースコアのみ |
| 電話番号 | string | Yes | E.164形式（+819012345678） |
| 通常出発予定時間 | time | No | HH:MM形式、5分単位 |
| 所属 | string | No | 最大100文字 |
| 備考 | string | No | 最大500文字 |

**データ整合性**: `LINE_ID`と`電話番号`は一意

### シート②：出発見守り_当日管理

| 列名 | データ型 | 必須 | 形式・制約 |
|------|----------|------|------------|
| 日付 | date | Yes | YYYY-MM-DD形式 |
| 氏名 | string | Yes | 最大100文字 |
| LINE_ID | string | Yes | 最大100文字 |
| 出発予定時間 | datetime | No | YYYY-MM-DD HH:MM:SS形式（JST） |
| 出発時間 | datetime | No | YYYY-MM-DD HH:MM:SS.SSS形式（JST） |
| 出発判定 | enum | No | "OK" / "遅れ返" / "要確認" / "管制対応" |
| 出発電話回数 | integer | No | 0 / 1 / 2 |
| 最終結果 | enum | No | "出勤OK" / "遅刻" / "穴埋め" / "未確定" |
| 管制メモ | string | No | 最大1000文字 |

**データ整合性**: `日付` + `LINE_ID`の組み合わせは一意（1日1人1レコード）

## APIエンドポイント

### POST /webhook/line

LINE Messaging APIのWebhookを受信

- Postbackイベント（出発報告ボタン）を処理
- メッセージイベント（出発予定時間登録）を処理
- LINE Messaging APIの署名検証を実装（必須）

### GET /health

健康チェック

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T08:30:00+09:00"
}
```

## エラーハンドリング

### LINE API

- 400系: ログ記録、ユーザーにエラーメッセージ送信、リトライなし
- 401/403: ログ記録、アラート通知、リトライなし
- 429/500: ログ記録、指数バックオフでリトライ（最大3回: 1s, 2s, 4s）
- タイムアウト: ログ記録、リトライ（最大3回）

### Twilio API

- 20003/21211/21608: ログ記録、スプレッドシートにエラーフラグ、リトライなし
- 20001: ログ記録、アラート通知、リトライなし
- 20429/500: ログ記録、指数バックオフでリトライ（最大3回: 1s, 2s, 4s）
- タイムアウト: ログ記録、リトライ（最大3回）
- 電話発信失敗時: ログ記録、スプレッドシートの`管制メモ`に「電話発信失敗」と記録、次の電話は通常通り実行

### Google Sheets API

- 400/401/403: ログ記録、アラート通知、リトライなし
- 429/500/503: ログ記録、指数バックオフでリトライ（最大5回: 1s, 2s, 4s, 8s, 16s）
- タイムアウト: ログ記録、リトライ（最大5回）
- 書き込み失敗時: ログ記録、リトライ（最大5回）、5回失敗した場合はメモリ上に保持して後で再試行（キューに保存）、アラート通知

### 共通

- すべてのAPI呼び出しでタイムアウトを設定（30秒）
- データ整合性エラー: スプレッドシートから取得したデータのバリデーション、不正なデータはログ記録し、デフォルト値を使用

## ログ設定

- ログレベル: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ログ出力先: ファイル（`./logs/app.log`、日次ローテーション）、コンソール（開発環境のみ）
- ログ形式: `[YYYY-MM-DD HH:mm:ss.SSS] [LEVEL] [MODULE] MESSAGE`
- 個人情報保護: ログには個人情報を含めない（LINE_IDはハッシュ化）

## 実装時の注意点

1. **タイムゾーン**: すべてJST（Asia/Tokyo）で処理
2. **日付境界**: 23:59:59 → 00:00:00は翌日として扱う
3. **重複防止**: 出発報告ボタンの重複押下をチェック
4. **電話キャンセル**: 電話中に出発報告があった場合、残りの電話を即座にキャンセル
5. **スケジューラー**: サーバー起動時に自動開始、過去のスケジュールは実行しない
6. **データバリデーション**: すべての入力データをバリデーション（正規表現、型チェック、範囲チェック）
7. **エラーログ**: すべてのエラーをログに記録
8. **環境変数**: 起動時に必須環境変数の存在をチェック

## 正規表現パターン

```python
PHONE_NUMBER_PATTERN = r'^\+[1-9]\d{1,14}$'  # 電話番号（E.164形式）
TIME_PATTERN = r'^([0-1]?[0-9]|2[0-3]):([0-5][05])$'  # 時刻（HH:MM、5分単位）
DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'  # 日付（YYYY-MM-DD）
LINE_ID_PATTERN = r'^[a-zA-Z0-9_]+$'  # LINE_ID（英数字とアンダースコア）
```

## 実装の優先順位

1. データモデル（Pydantic）の実装
2. 設定管理（config.py）の実装
3. ログ設定（utils/logger.py）の実装
4. Google Sheets Serviceの実装
5. LINE Serviceの実装
6. Twilio Serviceの実装
7. Departure Service（判定ロジック）の実装
8. Webhook Handlerの実装
9. スケジューラーの実装
10. FastAPIアプリケーション（main.py）の実装
11. エラーハンドリングの実装
12. テストの実装

## テスト要件

- 単体テスト: 判定ロジック、データバリデーション、エラーハンドリング
- 統合テスト: LINE API連携（モック）、Twilio API連携（モック）、Google Sheets API連携（テスト用スプレッドシート）
- エンドツーエンドテスト: 前日登録から当日出発報告までのフロー

---

**重要**: この仕様に従って実装してください。不明な点があれば、仕様書（SPECIFICATION.md）とアーキテクチャ設計書（ARCHITECTURE.md）を参照してください。

