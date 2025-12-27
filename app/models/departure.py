from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


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
