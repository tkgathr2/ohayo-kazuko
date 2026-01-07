# 環境変数の引き継ぎ方法

以前設定した環境変数を引き継ぐ方法です。

---

## 確認方法

### 1. 以前のプロジェクトディレクトリを確認

以前のプロジェクトディレクトリに`.env`ファイルがあるか確認してください：

```bash
# 以前のプロジェクトディレクトリで確認
ls -la .env
# または
dir .env
```

### 2. システム環境変数を確認

Windowsの場合、システム環境変数に設定されている可能性があります：

```powershell
# PowerShellで確認
$env:LINE_CHANNEL_ACCESS_TOKEN
$env:TWILIO_ACCOUNT_SID
$env:GOOGLE_SHEETS_SPREADSHEET_ID
```

### 3. 他の設定ファイルを確認

以下の場所に設定が残っている可能性があります：
- 親ディレクトリの`.env`ファイル
- 別のプロジェクトディレクトリ
- メモやドキュメントに記録された値

---

## 引き継ぎ手順

### 方法1: .envファイルから引き継ぐ

以前の`.env`ファイルがある場合：

```bash
# 以前の.envファイルをコピー
cp /path/to/old/project/.env .env

# または、内容をコピーして新しい.envファイルを作成
```

### 方法2: システム環境変数から引き継ぐ

システム環境変数に設定されている場合：

```powershell
# PowerShellで.envファイルを作成
@"
LINE_CHANNEL_ACCESS_TOKEN=$env:LINE_CHANNEL_ACCESS_TOKEN
LINE_CHANNEL_SECRET=$env:LINE_CHANNEL_SECRET
TWILIO_ACCOUNT_SID=$env:TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN=$env:TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER=$env:TWILIO_PHONE_NUMBER
GOOGLE_SHEETS_CREDENTIALS_JSON=$env:GOOGLE_SHEETS_CREDENTIALS_JSON
GOOGLE_SHEETS_SPREADSHEET_ID=$env:GOOGLE_SHEETS_SPREADSHEET_ID
CONTROL_LINE_ID=$env:CONTROL_LINE_ID
"@ | Out-File -FilePath .env -Encoding utf8
```

### 方法3: 手動で設定

以前の設定値をメモやドキュメントから確認し、`docs/ENV_TEMPLATE.md`を参考に`.env`ファイルを作成してください。

---

## 現在の状況

現在、このプロジェクトには`.env`ファイルが存在しません。

以下のいずれかの方法で環境変数を設定してください：

1. **以前の設定を引き継ぐ**（上記の方法1または2）
2. **新規に設定する**（`docs/ENV_TEMPLATE.md`を参考）

---

## 設定後の確認

環境変数を設定した後、セットアップ確認スクリプトを実行してください：

```bash
python scripts/verify_setup.py
```

すべての必須環境変数が設定され、Google Sheetsへの接続が成功することを確認してください。

---

**作成日**: 2026年1月4日

