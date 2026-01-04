# おはよう和子さん

キャストの出発予定時間・起床予定時間を管理するLINE Bot連携システム。

## 主な機能

- **出発予定時間の管理**: LINEメッセージで出発予定時間を登録・報告
- **起床予定時間の管理**: LINEメッセージで起床予定時間を登録・報告（ON/OFF切り替え可能）
- **リマインド通知**: 18:00-22:00に未登録者へリマインド送信
- **電話発信**: 予定時間を過ぎても報告がない場合、Twilioで電話発信
- **管制通知**: 未登録者・緊急アラートを管制に通知
- **Procastデータ連携**: Google DriveからProcastデータを取得し、翌日出勤者のみにリマインド

## 技術スタック

- **Python 3.11+**
- **FastAPI**: Webフレームワーク
- **APScheduler**: スケジュールジョブ管理
- **LINE Messaging API**: LINE Bot連携
- **Twilio**: 電話発信
- **Google Sheets API**: キャスト情報・出発記録の管理
- **Google Drive API**: Procastデータ取得

## セットアップ

### 1. 環境変数の設定

```bash
cp .env.example .env
# .envファイルを編集して環境変数を設定
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

### 3. Google Sheetsの設定

以下のシートを作成してください：

#### キャスト一覧シート

| 列名 | 説明 |
|------|------|
| 氏名 | キャストの氏名 |
| LINE_ID | LINEユーザーID |
| 電話番号 | 電話番号（+81形式） |
| 通常出発予定時間 | デフォルトの出発予定時間（HH:MM） |
| 起床予定時間登録ON/OFF | TRUE/FALSE |
| 通常起床予定時間 | デフォルトの起床予定時間（HH:MM） |
| 起床オフセット（分） | 起床予定時間のオフセット |

#### 出発予定時間_当日管理シート

| 列名 | 説明 |
|------|------|
| 日付 | YYYY-MM-DD形式 |
| 氏名 | キャストの氏名 |
| LINE_ID | LINEユーザーID |
| 出発予定時間 | 当日の出発予定時間 |
| 出発報告時刻 | 出発報告ボタン押下時刻 |
| 出発判定 | OK/遅れ返/要確認 |
| 出発電話発信回数 | 電話発信回数 |
| 起床予定時間 | 当日の起床予定時間 |
| 起床報告時刻 | 起床報告ボタン押下時刻 |
| 起床判定 | OK/遅れ返/要確認 |
| 起床電話発信回数 | 電話発信回数 |
| 最終結果 | OK/要管制 |

### 4. アプリケーションの起動

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## テスト

```bash
# テスト実行
python -m pytest app/tests/ -v

# カバレッジレポート
python -m pytest app/tests/ --cov=app --cov-report=html
```

## 動作確認

1. **出発予定時間の登録**: LINEメッセージ「出発 08:30」を送信
2. **起床予定時間の登録**: LINEメッセージ「起床 07:00」を送信
3. **出発報告**: 出発報告ボタンを押す
4. **起床報告**: 起床報告ボタンを押す

## ドキュメント

- `docs/DEPLOYMENT.md`: デプロイ手順書
- `CLAUDE_CODE_INSTRUCTIONS.md`: 実装指示書

## ライセンス

Private
