from datetime import time
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.utils.validators import LINE_ID_PATTERN, PHONE_NUMBER_PATTERN, TIME_PATTERN


class Cast(BaseModel):
    name: str = Field(..., max_length=100, description="氏名")
    line_id: str = Field(..., max_length=100, pattern=LINE_ID_PATTERN, description="LINE_ID")
    phone_number: str = Field(..., pattern=PHONE_NUMBER_PATTERN, description="電話番号（E.164形式）")
    default_departure_time: Optional[time] = Field(None, description="通常出発予定時間（HH:MM、5分単位）")
    department: Optional[str] = Field(None, max_length=100, description="所属")
    notes: Optional[str] = Field(None, max_length=500, description="備考")

    @field_validator("default_departure_time")
    @classmethod
    def validate_departure_time(cls, value: Optional[time]) -> Optional[time]:
        if value is None:
            return value
        if value.minute % 5 != 0:
            raise ValueError("default_departure_time must be 5-minute increments")
        return value
