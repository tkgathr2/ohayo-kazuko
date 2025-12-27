# 蜃ｺ逋ｺ隕句ｮ医ｊ蜥悟ｭ舌＆繧・- 繧ｳ繝ｼ繝・ャ繧ｯ繧ｹ螳溯｣・・繝ｭ繝ｳ繝励ヨ

## 繝励Ο繧ｸ繧ｧ繧ｯ繝域ｦりｦ・

蜃ｺ蜍､蜑阪・遒ｺ隱阪ｒ閾ｪ蜍募喧縺吶ｋ繧ｷ繧ｹ繝・Β縲悟・逋ｺ隕句ｮ医ｊ蜥悟ｭ舌＆繧薙阪ｒ螳溯｣・＠縺ｦ縺上□縺輔＞縲・

**蝓ｺ譛ｬ譁ｹ驥・*:
- 蛻､螳壹・蜃ｺ逋ｺ蝣ｱ蜻翫・繧ｿ繝ｳ繧呈款縺励◆譎ょ綾縺ｮ縺ｿ繧剃ｽｿ逕ｨ
- 髮ｻ隧ｱ縺ｮ逹菫｡繝ｻ蠢懃ｭ斐・逡吝ｮ磯崕縺ｯ蛻､螳壹↓菴ｿ繧上↑縺・
- 邂｡蛻ｶ縺ｯ譛邨よｮｵ髫弱・縺ｿ莉句・

## 謚陦薙せ繧ｿ繝・け

- **繝舌ャ繧ｯ繧ｨ繝ｳ繝・*: FastAPI 0.104.0+
- **險隱・*: Python 3.11+
- **繧ｹ繧ｱ繧ｸ繝･繝ｼ繝ｩ繝ｼ**: APScheduler 3.10.0+
- **HTTP繧ｯ繝ｩ繧､繧｢繝ｳ繝・*: httpx
- **繝・・繧ｿ讀懆ｨｼ**: Pydantic 2.0+
- **螟夜ΚAPI**: LINE Messaging API v2, Twilio Voice API, Google Sheets API v4

## 繝・ぅ繝ｬ繧ｯ繝医Μ讒矩

```
kazuko_departure_watch/
笏懌楳笏 app/
笏・  笏懌楳笏 __init__.py
笏・  笏懌楳笏 main.py                 # FastAPI繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧ｨ繝ｳ繝医Μ繝ｼ繝昴う繝ｳ繝・
笏・  笏懌楳笏 config.py               # 險ｭ螳夂ｮ｡逅・
笏・  笏懌楳笏 models/
笏・  笏・  笏懌楳笏 __init__.py
笏・  笏・  笏懌楳笏 cast.py            # 繧ｭ繝｣繧ｹ繝医Δ繝・Ν
笏・  笏・  笏披楳笏 departure.py       # 蜃ｺ逋ｺ邂｡逅・Δ繝・Ν
笏・  笏懌楳笏 services/
笏・  笏・  笏懌楳笏 __init__.py
笏・  笏・  笏懌楳笏 line_service.py    # LINE API騾｣謳ｺ
笏・  笏・  笏懌楳笏 twilio_service.py  # Twilio API騾｣謳ｺ
笏・  笏・  笏懌楳笏 spreadsheet_service.py  # Google Sheets騾｣謳ｺ
笏・  笏・  笏懌楳笏 notification_service.py # 騾夂衍繧ｵ繝ｼ繝薙せ
笏・  笏・  笏懌楳笏 phone_service.py   # 髮ｻ隧ｱ繧ｵ繝ｼ繝薙せ
笏・  笏・  笏披楳笏 departure_service.py   # 蜃ｺ逋ｺ蛻､螳壹し繝ｼ繝薙せ
笏・  笏懌楳笏 handlers/
笏・  笏・  笏懌楳笏 __init__.py
笏・  笏・  笏披楳笏 webhook_handler.py # LINE Webhook蜃ｦ逅・
笏・  笏懌楳笏 schedulers/
笏・  笏・  笏懌楳笏 __init__.py
笏・  笏・  笏披楳笏 job_scheduler.py   # 繧ｹ繧ｱ繧ｸ繝･繝ｼ繝ｩ繝ｼ險ｭ螳・
笏・  笏懌楳笏 utils/
笏・  笏・  笏懌楳笏 __init__.py
笏・  笏・  笏懌楳笏 logger.py          # 繝ｭ繧ｰ險ｭ螳・
笏・  笏・  笏懌楳笏 validators.py      # 繝舌Μ繝・・繧ｷ繝ｧ繝ｳ
笏・  笏・  笏披楳笏 error_handler.py   # 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ
笏・  笏披楳笏 tests/
笏・      笏懌楳笏 __init__.py
笏・      笏懌楳笏 test_models.py
笏・      笏懌楳笏 test_services.py
笏・      笏披楳笏 test_handlers.py
笏懌楳笏 logs/                       # 繝ｭ繧ｰ繝輔ぃ繧､繝ｫ・・gitignore・・
笏懌楳笏 .env.example               # 迺ｰ蠅・､画焚繝・Φ繝励Ξ繝ｼ繝・
笏懌楳笏 .gitignore
笏懌楳笏 requirements.txt           # 萓晏ｭ倬未菫・
笏披楳笏 README.md
```

## 繝・・繧ｿ繝｢繝・Ν

### Cast・医く繝｣繧ｹ繝茨ｼ・

```python
from datetime import time
from typing import Optional
from pydantic import BaseModel, Field, validator

class Cast(BaseModel):
    name: str = Field(..., max_length=100, description="豌丞錐")
    line_id: str = Field(..., max_length=100, regex=r'^[a-zA-Z0-9_]+$', description="LINE_ID")
    phone_number: str = Field(..., regex=r'^\+[1-9]\d{1,14}$', description="髮ｻ隧ｱ逡ｪ蜿ｷ・・.164蠖｢蠑擾ｼ・)
    default_departure_time: Optional[time] = Field(None, description="騾壼ｸｸ蜃ｺ逋ｺ莠亥ｮ壽凾髢難ｼ・H:MM縲・蛻・腰菴搾ｼ・)
    department: Optional[str] = Field(None, max_length=100, description="謇螻・)
    notes: Optional[str] = Field(None, max_length=500, description="蛯呵・)
```

### DepartureRecord・亥・逋ｺ邂｡逅・ｼ・

```python
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class DepartureStatus(str, Enum):
    OK = "OK"
    DELAYED = "驕・ｌ霑・
    NEED_CHECK = "隕∫｢ｺ隱・
    CONTROL = "邂｡蛻ｶ蟇ｾ蠢・

class FinalResult(str, Enum):
    ATTENDANCE_OK = "蜃ｺ蜍､OK"
    LATE = "驕・綾"
    FILLED = "遨ｴ蝓九ａ"
    UNDETERMINED = "譛ｪ遒ｺ螳・

class DepartureRecord(BaseModel):
    date: date = Field(..., description="譌･莉假ｼ・YYY-MM-DD・・)
    name: str = Field(..., max_length=100, description="豌丞錐")
    line_id: str = Field(..., max_length=100, description="LINE_ID")
    scheduled_departure_time: Optional[datetime] = Field(None, description="蜃ｺ逋ｺ莠亥ｮ壽凾髢難ｼ・ST・・)
    actual_departure_time: Optional[datetime] = Field(None, description="蜃ｺ逋ｺ譎る俣・・ST縲√Α繝ｪ遘偵∪縺ｧ・・)
    departure_status: Optional[DepartureStatus] = Field(None, description="蜃ｺ逋ｺ蛻､螳・)
    phone_call_count: int = Field(0, ge=0, le=2, description="蜃ｺ逋ｺ髮ｻ隧ｱ蝗樊焚・・/1/2・・)
    final_result: Optional[FinalResult] = Field(None, description="譛邨らｵ先棡")
    control_notes: Optional[str] = Field(None, max_length=1000, description="邂｡蛻ｶ繝｡繝｢")
```

## 迺ｰ蠅・､画焚

### 蠢・育腸蠅・､画焚

```python
LINE_CHANNEL_ACCESS_TOKEN: str  # LINE Messaging API縺ｮ繧｢繧ｯ繧ｻ繧ｹ繝医・繧ｯ繝ｳ
LINE_CHANNEL_SECRET: str        # LINE Messaging API縺ｮ繧ｷ繝ｼ繧ｯ繝ｬ繝・ヨ
TWILIO_ACCOUNT_SID: str         # Twilio繧｢繧ｫ繧ｦ繝ｳ繝・ID・域ｭ｣隕剰｡ｨ迴ｾ: ^AC[a-z0-9]{32}$・・
TWILIO_AUTH_TOKEN: str          # Twilio隱崎ｨｼ繝医・繧ｯ繝ｳ
TWILIO_PHONE_NUMBER: str        # Twilio逋ｺ菫｡蜈・崕隧ｱ逡ｪ蜿ｷ・・.164蠖｢蠑擾ｼ・
GOOGLE_SHEETS_CREDENTIALS_JSON: str  # Google Sheets API隱崎ｨｼ諠・ｱ・・SON譁・ｭ怜・・・
GOOGLE_SHEETS_SPREADSHEET_ID: str    # 繧ｹ繝励Ξ繝・ラ繧ｷ繝ｼ繝・D
TZ: str = "Asia/Tokyo"          # 繧ｿ繧､繝繧ｾ繝ｼ繝ｳ
```

### 繧ｪ繝励す繝ｧ繝ｳ迺ｰ蠅・､画焚

```python
LOG_LEVEL: str = "INFO"
LOG_FILE: str = "./logs/app.log"
API_HOST: str = "0.0.0.0"
API_PORT: int = 8000
```

## 荳ｻ隕∵ｩ溯・隕∽ｻｶ

### 1. 蜑肴律蜃ｺ逋ｺ莠亥ｮ壽凾髢鍋匳骭ｲ

- LINE縺ｧ譎や・蛻・・2繧ｿ繝・・縺ｧ逋ｻ骭ｲ・・蛻・腰菴阪・縺ｿ・・
- 繝・・繧ｿ蠖｢蠑・ 譎ゑｼ・-23・峨∝・・・, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55・・
- 譌･莉倥・逋ｻ骭ｲ譌･縺ｮ鄙梧律・医す繧ｹ繝・Β縺瑚・蜍募愛螳夲ｼ・
- Google繧ｹ繝励Ξ繝・ラ繧ｷ繝ｼ繝医悟・逋ｺ隕句ｮ医ｊ_蠖捺律邂｡逅・阪↓菫晏ｭ・

### 2. 蜑肴律繝ｪ繝槭う繝ｳ繝会ｼ医せ繧ｱ繧ｸ繝･繝ｼ繝ｩ繝ｼ・・

| 譎ょ綾 | 蜃ｦ逅・|
|------|------|
| 20:00 JST | 譛ｪ逋ｻ骭ｲ閠・↓LINE騾夂衍 |
| 21:00 JST | 譛ｪ逋ｻ骭ｲ閠・↓LINE騾夂衍 |
| 22:00 JST | 譛ｪ逋ｻ骭ｲ閠・↓LINE騾夂衍 |
| 22:30 JST | 邂｡蛻ｶ縺ｸ譛ｪ逋ｻ骭ｲ閠・夂衍・井ｺｺ謨ｰ・区ｰ丞錐・・|
| 23:00 JST | 譛ｪ逋ｻ骭ｲ閠・↓譛邨・INE騾夂衍 |
| 24:00 JST | 騾壼ｸｸ蜃ｺ逋ｺ莠亥ｮ壽凾髢薙ｒ閾ｪ蜍墓治逕ｨ・育┌縺代ｌ縺ｰ邂｡蛻ｶ騾夂衍・・|

### 3. 蠖捺律蜃ｺ逋ｺ蝣ｱ蜻・

- LINE縺ｮ縲悟・逋ｺ蝣ｱ蜻翫阪・繧ｿ繝ｳ・・ostback・峨ｒ謚ｼ縺・
- 驥崎､・款荳九・縲梧里縺ｫ蜃ｺ逋ｺ蝣ｱ蜻頑ｸ医∩縺ｧ縺吶阪→陦ｨ遉ｺ縲∝・逅・せ繧ｭ繝・・
- 蛻､螳壹Ο繧ｸ繝・け:
  - `蜃ｺ逋ｺ譎る俣 <= 蜃ｺ逋ｺ莠亥ｮ壽凾髢伝 竊・"OK"・井ｽ輔ｂ縺励↑縺・ｼ・
  - `蜃ｺ逋ｺ譎る俣 > 蜃ｺ逋ｺ莠亥ｮ壽凾髢伝 竊・"驕・ｌ霑・・医Ο繧ｰ縺ｮ縺ｿ・・
  - `蜃ｺ逋ｺ莠亥ｮ壽凾髢薙∪縺ｧ縺ｫ譛ｪ蝣ｱ蜻柿 竊・"隕∫｢ｺ隱・・郁・蜍暮崕隧ｱ縺ｸ・・

**驥崎ｦ・*: 譎ょ綾豈碑ｼ・・遘貞腰菴搾ｼ医Α繝ｪ遘偵・蛻・ｊ謐ｨ縺ｦ・・

### 4. 閾ｪ蜍暮崕隧ｱ・亥・逋ｺ莠亥ｮ壽凾髢薙・1蛻・ｾ後°繧蛾幕蟋具ｼ・

- **髮ｻ隧ｱ竭**: 5蛻・♀縺・ﾃ・5蝗橸ｼ育ｴ・5蛻・ｼ・
- **髮ｻ隧ｱ竭｡**: 3蛻・♀縺・ﾃ・10蝗橸ｼ育ｴ・0蛻・ｼ・
- **蜷郁ｨ・*: 邏・5蛻・
- 髻ｳ螢ｰ繝｡繝・そ繝ｼ繧ｸ: 縲後♀縺ｯ繧医≧縺斐＊縺・∪縺吶ょ・逋ｺ隕句ｮ医ｊ蜥悟ｭ舌＆繧薙〒縺吶よ悽譌･縺ｮ蜃ｺ逋ｺ蝣ｱ蜻翫ｒ縺企｡倥＞縺励∪縺吶・INE縺ｮ蜃ｺ逋ｺ蝣ｱ蜻翫・繧ｿ繝ｳ繧呈款縺励※縺上□縺輔＞縲ゅ・
- 髮ｻ隧ｱ荳ｭ縺ｫ蜃ｺ逋ｺ蝣ｱ蜻翫′縺ゅ▲縺溷ｴ蜷医∵ｮ九ｊ縺ｮ髮ｻ隧ｱ縺ｯ蜊ｳ蠎ｧ縺ｫ繧ｭ繝｣繝ｳ繧ｻ繝ｫ
- **驥崎ｦ・*: 髮ｻ隧ｱ縺ｮ邨先棡・育捩菫｡繝ｻ蠢懃ｭ斐・逡吝ｮ磯崕・峨・蛻､螳壹↓菴ｿ繧上↑縺・

### 5. 邂｡蛻ｶ騾夂衍

- **譚｡莉ｶ**: 髮ｻ隧ｱ竭竭｡螳瑚ｵｰ蠕後ｂ蜃ｺ逋ｺ蝣ｱ蜻翫↑縺・
- **繧ｿ繧､繝溘Φ繧ｰ**: 髮ｻ隧ｱ竭｡縺ｮ譛蠕後・髮ｻ隧ｱ縺檎ｵゆｺ・＠縺滓凾轤ｹ
- **蜀・ｮｹ**: 豌丞錐縲∝・逋ｺ莠亥ｮ壽凾髢薙∫樟蝨ｨ譎ょ綾縲・崕隧ｱ竭竭｡縺ｮ螳御ｺ・憾豕・

## 蛻､螳壹Ο繧ｸ繝・け・・ython螳溯｣・ｼ・

```python
from datetime import datetime
from typing import Optional

def judge_departure(actual_time: Optional[datetime], scheduled_time: datetime, current_time: datetime) -> Optional[str]:
    """
    蜃ｺ逋ｺ蛻､螳壹Ο繧ｸ繝・け
    
    Args:
        actual_time: 蜃ｺ逋ｺ蝣ｱ蜻翫・繧ｿ繝ｳ謚ｼ荳区凾蛻ｻ・・ST縲¨one縺ｮ蝣ｴ蜷医・譛ｪ蝣ｱ蜻奇ｼ・
        scheduled_time: 蜃ｺ逋ｺ莠亥ｮ壽凾髢難ｼ・ST・・
        current_time: 迴ｾ蝨ｨ譎ょ綾・・ST・・
    
    Returns:
        "OK" / "驕・ｌ霑・ / "隕∫｢ｺ隱・ / None・医∪縺蛻､螳壹〒縺阪↑縺・ｼ・
    """
    if actual_time is None:
        # 蜃ｺ逋ｺ蝣ｱ蜻翫′辟｡縺・
        if current_time > scheduled_time:
            return "隕∫｢ｺ隱・
        else:
            return None  # 縺ｾ縺蛻､螳壹〒縺阪↑縺・
    
    # 譎ょ綾豈碑ｼ・ｼ育ｧ貞腰菴阪√Α繝ｪ遘偵・蛻・ｊ謐ｨ縺ｦ・・
    actual_seconds = actual_time.replace(microsecond=0)
    scheduled_seconds = scheduled_time.replace(microsecond=0)
    
    if actual_seconds <= scheduled_seconds:
        return "OK"
    else:
        return "驕・ｌ霑・
```

## Google繧ｹ繝励Ξ繝・ラ繧ｷ繝ｼ繝域ｧ矩

### 繧ｷ繝ｼ繝遺蔵・壹く繝｣繧ｹ繝井ｸ隕ｧ

| 蛻怜錐 | 繝・・繧ｿ蝙・| 蠢・・| 蠖｢蠑上・蛻ｶ邏・|
|------|----------|------|------------|
| 豌丞錐 | string | Yes | 譛螟ｧ100譁・ｭ・|
| LINE_ID | string | Yes | 譛螟ｧ100譁・ｭ励∬恭謨ｰ蟄励→繧｢繝ｳ繝繝ｼ繧ｹ繧ｳ繧｢縺ｮ縺ｿ |
| 髮ｻ隧ｱ逡ｪ蜿ｷ | string | Yes | E.164蠖｢蠑擾ｼ・819012345678・・|
| 騾壼ｸｸ蜃ｺ逋ｺ莠亥ｮ壽凾髢・| time | No | HH:MM蠖｢蠑上・蛻・腰菴・|
| 謇螻・| string | No | 譛螟ｧ100譁・ｭ・|
| 蛯呵・| string | No | 譛螟ｧ500譁・ｭ・|

**繝・・繧ｿ謨ｴ蜷域ｧ**: `LINE_ID`縺ｨ`髮ｻ隧ｱ逡ｪ蜿ｷ`縺ｯ荳諢・

### 繧ｷ繝ｼ繝遺贈・壼・逋ｺ隕句ｮ医ｊ_蠖捺律邂｡逅・

| 蛻怜錐 | 繝・・繧ｿ蝙・| 蠢・・| 蠖｢蠑上・蛻ｶ邏・|
|------|----------|------|------------|
| 譌･莉・| date | Yes | YYYY-MM-DD蠖｢蠑・|
| 豌丞錐 | string | Yes | 譛螟ｧ100譁・ｭ・|
| LINE_ID | string | Yes | 譛螟ｧ100譁・ｭ・|
| 蜃ｺ逋ｺ莠亥ｮ壽凾髢・| datetime | No | YYYY-MM-DD HH:MM:SS蠖｢蠑擾ｼ・ST・・|
| 蜃ｺ逋ｺ譎る俣 | datetime | No | YYYY-MM-DD HH:MM:SS.SSS蠖｢蠑擾ｼ・ST・・|
| 蜃ｺ逋ｺ蛻､螳・| enum | No | "OK" / "驕・ｌ霑・ / "隕∫｢ｺ隱・ / "邂｡蛻ｶ蟇ｾ蠢・ |
| 蜃ｺ逋ｺ髮ｻ隧ｱ蝗樊焚 | integer | No | 0 / 1 / 2 |
| 譛邨らｵ先棡 | enum | No | "蜃ｺ蜍､OK" / "驕・綾" / "遨ｴ蝓九ａ" / "譛ｪ遒ｺ螳・ |
| 邂｡蛻ｶ繝｡繝｢ | string | No | 譛螟ｧ1000譁・ｭ・|

**繝・・繧ｿ謨ｴ蜷域ｧ**: `譌･莉倭 + `LINE_ID`縺ｮ邨・∩蜷医ｏ縺帙・荳諢擾ｼ・譌･1莠ｺ1繝ｬ繧ｳ繝ｼ繝会ｼ・

## API繧ｨ繝ｳ繝峨・繧､繝ｳ繝・

### POST /webhook/line

LINE Messaging API縺ｮWebhook繧貞女菫｡

- Postback繧､繝吶Φ繝茨ｼ亥・逋ｺ蝣ｱ蜻翫・繧ｿ繝ｳ・峨ｒ蜃ｦ逅・
- 繝｡繝・そ繝ｼ繧ｸ繧､繝吶Φ繝茨ｼ亥・逋ｺ莠亥ｮ壽凾髢鍋匳骭ｲ・峨ｒ蜃ｦ逅・
- LINE Messaging API縺ｮ鄂ｲ蜷肴､懆ｨｼ繧貞ｮ溯｣・ｼ亥ｿ・茨ｼ・

### GET /health

蛛･蠎ｷ繝√ぉ繝・け

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T08:30:00+09:00"
}
```

## 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ

### LINE API

- 400邉ｻ: 繝ｭ繧ｰ險倬鹸縲√Θ繝ｼ繧ｶ繝ｼ縺ｫ繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ騾∽ｿ｡縲√Μ繝医Λ繧､縺ｪ縺・
- 401/403: 繝ｭ繧ｰ險倬鹸縲√い繝ｩ繝ｼ繝磯夂衍縲√Μ繝医Λ繧､縺ｪ縺・
- 429/500: 繝ｭ繧ｰ險倬鹸縲∵欠謨ｰ繝舌ャ繧ｯ繧ｪ繝輔〒繝ｪ繝医Λ繧､・域怙螟ｧ3蝗・ 1s, 2s, 4s・・
- 繧ｿ繧､繝繧｢繧ｦ繝・ 繝ｭ繧ｰ險倬鹸縲√Μ繝医Λ繧､・域怙螟ｧ3蝗橸ｼ・

### Twilio API

- 20003/21211/21608: 繝ｭ繧ｰ險倬鹸縲√せ繝励Ξ繝・ラ繧ｷ繝ｼ繝医↓繧ｨ繝ｩ繝ｼ繝輔Λ繧ｰ縲√Μ繝医Λ繧､縺ｪ縺・
- 20001: 繝ｭ繧ｰ險倬鹸縲√い繝ｩ繝ｼ繝磯夂衍縲√Μ繝医Λ繧､縺ｪ縺・
- 20429/500: 繝ｭ繧ｰ險倬鹸縲∵欠謨ｰ繝舌ャ繧ｯ繧ｪ繝輔〒繝ｪ繝医Λ繧､・域怙螟ｧ3蝗・ 1s, 2s, 4s・・
- 繧ｿ繧､繝繧｢繧ｦ繝・ 繝ｭ繧ｰ險倬鹸縲√Μ繝医Λ繧､・域怙螟ｧ3蝗橸ｼ・
- 髮ｻ隧ｱ逋ｺ菫｡螟ｱ謨玲凾: 繝ｭ繧ｰ險倬鹸縲√せ繝励Ξ繝・ラ繧ｷ繝ｼ繝医・`邂｡蛻ｶ繝｡繝｢`縺ｫ縲碁崕隧ｱ逋ｺ菫｡螟ｱ謨励阪→險倬鹸縲∵ｬ｡縺ｮ髮ｻ隧ｱ縺ｯ騾壼ｸｸ騾壹ｊ螳溯｡・

### Google Sheets API

- 400/401/403: 繝ｭ繧ｰ險倬鹸縲√い繝ｩ繝ｼ繝磯夂衍縲√Μ繝医Λ繧､縺ｪ縺・
- 429/500/503: 繝ｭ繧ｰ險倬鹸縲∵欠謨ｰ繝舌ャ繧ｯ繧ｪ繝輔〒繝ｪ繝医Λ繧､・域怙螟ｧ5蝗・ 1s, 2s, 4s, 8s, 16s・・
- 繧ｿ繧､繝繧｢繧ｦ繝・ 繝ｭ繧ｰ險倬鹸縲√Μ繝医Λ繧､・域怙螟ｧ5蝗橸ｼ・
- 譖ｸ縺崎ｾｼ縺ｿ螟ｱ謨玲凾: 繝ｭ繧ｰ險倬鹸縲√Μ繝医Λ繧､・域怙螟ｧ5蝗橸ｼ峨・蝗槫､ｱ謨励＠縺溷ｴ蜷医・繝｡繝｢繝ｪ荳翫↓菫晄戟縺励※蠕後〒蜀崎ｩｦ陦鯉ｼ医く繝･繝ｼ縺ｫ菫晏ｭ假ｼ峨√い繝ｩ繝ｼ繝磯夂衍

### 蜈ｱ騾・

- 縺吶∋縺ｦ縺ｮAPI蜻ｼ縺ｳ蜃ｺ縺励〒繧ｿ繧､繝繧｢繧ｦ繝医ｒ險ｭ螳夲ｼ・0遘抵ｼ・
- 繝・・繧ｿ謨ｴ蜷域ｧ繧ｨ繝ｩ繝ｼ: 繧ｹ繝励Ξ繝・ラ繧ｷ繝ｼ繝医°繧牙叙蠕励＠縺溘ョ繝ｼ繧ｿ縺ｮ繝舌Μ繝・・繧ｷ繝ｧ繝ｳ縲∽ｸ肴ｭ｣縺ｪ繝・・繧ｿ縺ｯ繝ｭ繧ｰ險倬鹸縺励√ョ繝輔か繝ｫ繝亥､繧剃ｽｿ逕ｨ

## 繝ｭ繧ｰ險ｭ螳・

- 繝ｭ繧ｰ繝ｬ繝吶Ν: DEBUG, INFO, WARNING, ERROR, CRITICAL
- 繝ｭ繧ｰ蜃ｺ蜉帛・: 繝輔ぃ繧､繝ｫ・・./logs/app.log`縲∵律谺｡繝ｭ繝ｼ繝・・繧ｷ繝ｧ繝ｳ・峨√さ繝ｳ繧ｽ繝ｼ繝ｫ・磯幕逋ｺ迺ｰ蠅・・縺ｿ・・
- 繝ｭ繧ｰ蠖｢蠑・ `[YYYY-MM-DD HH:mm:ss.SSS] [LEVEL] [MODULE] MESSAGE`
- 蛟倶ｺｺ諠・ｱ菫晁ｭｷ: 繝ｭ繧ｰ縺ｫ縺ｯ蛟倶ｺｺ諠・ｱ繧貞性繧√↑縺・ｼ・INE_ID縺ｯ繝上ャ繧ｷ繝･蛹厄ｼ・

## 螳溯｣・凾縺ｮ豕ｨ諢冗せ

1. **繧ｿ繧､繝繧ｾ繝ｼ繝ｳ**: 縺吶∋縺ｦJST・・sia/Tokyo・峨〒蜃ｦ逅・
2. **譌･莉伜｢・阜**: 23:59:59 竊・00:00:00縺ｯ鄙梧律縺ｨ縺励※謇ｱ縺・
3. **驥崎､・亟豁｢**: 蜃ｺ逋ｺ蝣ｱ蜻翫・繧ｿ繝ｳ縺ｮ驥崎､・款荳九ｒ繝√ぉ繝・け
4. **髮ｻ隧ｱ繧ｭ繝｣繝ｳ繧ｻ繝ｫ**: 髮ｻ隧ｱ荳ｭ縺ｫ蜃ｺ逋ｺ蝣ｱ蜻翫′縺ゅ▲縺溷ｴ蜷医∵ｮ九ｊ縺ｮ髮ｻ隧ｱ繧貞叉蠎ｧ縺ｫ繧ｭ繝｣繝ｳ繧ｻ繝ｫ
5. **繧ｹ繧ｱ繧ｸ繝･繝ｼ繝ｩ繝ｼ**: 繧ｵ繝ｼ繝舌・襍ｷ蜍墓凾縺ｫ閾ｪ蜍暮幕蟋九・℃蜴ｻ縺ｮ繧ｹ繧ｱ繧ｸ繝･繝ｼ繝ｫ縺ｯ螳溯｡後＠縺ｪ縺・
6. **繝・・繧ｿ繝舌Μ繝・・繧ｷ繝ｧ繝ｳ**: 縺吶∋縺ｦ縺ｮ蜈･蜉帙ョ繝ｼ繧ｿ繧偵ヰ繝ｪ繝・・繧ｷ繝ｧ繝ｳ・域ｭ｣隕剰｡ｨ迴ｾ縲∝梛繝√ぉ繝・け縲∫ｯ・峇繝√ぉ繝・け・・
7. **繧ｨ繝ｩ繝ｼ繝ｭ繧ｰ**: 縺吶∋縺ｦ縺ｮ繧ｨ繝ｩ繝ｼ繧偵Ο繧ｰ縺ｫ險倬鹸
8. **迺ｰ蠅・､画焚**: 襍ｷ蜍墓凾縺ｫ蠢・育腸蠅・､画焚縺ｮ蟄伜惠繧偵メ繧ｧ繝・け

## 豁｣隕剰｡ｨ迴ｾ繝代ち繝ｼ繝ｳ

```python
PHONE_NUMBER_PATTERN = r'^\+[1-9]\d{1,14}$'  # 髮ｻ隧ｱ逡ｪ蜿ｷ・・.164蠖｢蠑擾ｼ・
TIME_PATTERN = r'^([0-1]?[0-9]|2[0-3]):([0-5][05])$'  # 譎ょ綾・・H:MM縲・蛻・腰菴搾ｼ・
DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'  # 譌･莉假ｼ・YYY-MM-DD・・
LINE_ID_PATTERN = r'^[a-zA-Z0-9_]+$'  # LINE_ID・郁恭謨ｰ蟄励→繧｢繝ｳ繝繝ｼ繧ｹ繧ｳ繧｢・・
```

## 螳溯｣・・蜆ｪ蜈磯・ｽ・

1. 繝・・繧ｿ繝｢繝・Ν・・ydantic・峨・螳溯｣・
2. 險ｭ螳夂ｮ｡逅・ｼ・onfig.py・峨・螳溯｣・
3. 繝ｭ繧ｰ險ｭ螳夲ｼ・tils/logger.py・峨・螳溯｣・
4. Google Sheets Service縺ｮ螳溯｣・
5. LINE Service縺ｮ螳溯｣・
6. Twilio Service縺ｮ螳溯｣・
7. Departure Service・亥愛螳壹Ο繧ｸ繝・け・峨・螳溯｣・
8. Webhook Handler縺ｮ螳溯｣・
9. 繧ｹ繧ｱ繧ｸ繝･繝ｼ繝ｩ繝ｼ縺ｮ螳溯｣・
10. FastAPI繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ・・ain.py・峨・螳溯｣・
11. 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ螳溯｣・
12. 繝・せ繝医・螳溯｣・

## 繝・せ繝郁ｦ∽ｻｶ

- 蜊倅ｽ薙ユ繧ｹ繝・ 蛻､螳壹Ο繧ｸ繝・け縲√ョ繝ｼ繧ｿ繝舌Μ繝・・繧ｷ繝ｧ繝ｳ縲√お繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ
- 邨ｱ蜷医ユ繧ｹ繝・ LINE API騾｣謳ｺ・医Δ繝・け・峨ゝwilio API騾｣謳ｺ・医Δ繝・け・峨；oogle Sheets API騾｣謳ｺ・医ユ繧ｹ繝育畑繧ｹ繝励Ξ繝・ラ繧ｷ繝ｼ繝茨ｼ・
- 繧ｨ繝ｳ繝峨ヤ繝ｼ繧ｨ繝ｳ繝峨ユ繧ｹ繝・ 蜑肴律逋ｻ骭ｲ縺九ｉ蠖捺律蜃ｺ逋ｺ蝣ｱ蜻翫∪縺ｧ縺ｮ繝輔Ο繝ｼ

---

**驥崎ｦ・*: 縺薙・莉墓ｧ倥↓蠕薙▲縺ｦ螳溯｣・＠縺ｦ縺上□縺輔＞縲ゆｸ肴・縺ｪ轤ｹ縺後≠繧後・縲∽ｻ墓ｧ俶嶌・・PECIFICATION.md・峨→繧｢繝ｼ繧ｭ繝・け繝√Ε險ｭ險域嶌・・RCHITECTURE.md・峨ｒ蜿ら・縺励※縺上□縺輔＞縲・


