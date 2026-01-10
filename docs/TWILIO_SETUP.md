# Twilio設定情報

このドキュメントには、Twilioアカウントの設定情報と規制バンドル申請の情報を記録します。

## アカウント情報

### アカウントSID
```
AC6e27b4588461b5a5307ea91707e12dd4
```

## 規制バンドル申請（日本：国内 - ビジネス）

### 申請日時
2026年1月8日 9時50分40秒

### 規制バンドルSID
```
BU43b4e1073590c81a0a87238c9a7c04
```

### 規制バンドルURL
https://console.twilio.com/us1/develop/phone-numbers/regulatory-compliance/bundles/BU43b4e1073590c81a0a87238c9a7c04

### ステータス
**審査待ち**（2026年1月8日時点）

Twilioによる審査が完了するまで待機してください。審査完了後、日本の電話番号を取得できるようになります。

---

## 環境変数への反映

規制バンドルが承認され、電話番号を取得したら、以下の環境変数を設定してください：

```env
# Twilio Voice API
TWILIO_ACCOUNT_SID=AC6e27b4588461b5a5307ea91707e12dd4
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+819012345678  # 取得した電話番号を設定
```

---

## 次のステップ

1. **規制バンドル審査完了を待つ**
   - Twilio Consoleで規制バンドルのステータスを確認
   - 承認されたら通知が来ます

2. **電話番号の取得**
   - 規制バンドルが承認されたら、Twilio Consoleで日本の電話番号を検索・購入
   - 電話番号をE.164形式（例: `+819012345678`）で取得

3. **Auth Tokenの取得**
   - Twilio Consoleの **Account Info** から認証トークンを取得
   - セキュリティのため、定期的にローテーションを推奨

4. **環境変数の設定**
   - `.env`ファイルに上記の環境変数を設定
   - `python scripts/verify_setup.py` で設定を確認

---

## 参考リンク

- [Twilio Console](https://www.twilio.com/console)
- [Twilio Regulatory Compliance](https://www.twilio.com/docs/phone-numbers/regulatory-compliance)
- [日本での電話番号取得ガイド](https://www.twilio.com/docs/phone-numbers/buy/searching/buying-a-phone-number-in-japan)
