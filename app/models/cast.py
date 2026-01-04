"""キャストモデル"""
from datetime import time
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.utils.validators import LINE_ID_PATTERN, PHONE_NUMBER_PATTERN


class Cast(BaseModel):
    """キャスト情報モデル"""
    name: str = Field(..., max_length=100, description="氏名")
    line_id: str = Field(..., max_length=100, pattern=LINE_ID_PATTERN, description="LINE ID")
    phone_number: str = Field(..., pattern=PHONE_NUMBER_PATTERN, description="電話番号（E.164形式）")
    default_departure_time: Optional[time] = Field(None, description="通常出発予定時間（5分単位）")

    # 起床予定時間設定
    wakeup_time_registration_enabled: bool = Field(False, description="起床予定時間登録機能のON/OFF")
    default_wakeup_time: Optional[time] = Field(None, description="通常起床予定時間（5分単位）")
    wakeup_offset_minutes: int = Field(0, description="起床予定時間のオフセット（分）")

    @field_validator("default_departure_time", "default_wakeup_time")
    @classmethod
    def validate_time_5min(cls, v: Optional[time]) -> Optional[time]:
        """時刻は5分単位で指定"""
        if v is None:
            return v
        if v.minute % 5 != 0:
            raise ValueError("時刻は5分単位で指定してください")
        return v
