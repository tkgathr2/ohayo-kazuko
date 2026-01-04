"""出発/起床管理モデル"""
from datetime import datetime, time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DepartureStatus(str, Enum):
    """出発ステータス"""
    OK = "OK"
    DELAYED = "遅れ返"
    NEED_CHECK = "要確認"


class WakeupStatus(str, Enum):
    """起床ステータス"""
    OK = "OK"
    DELAYED = "遅れ返"
    NEED_CHECK = "要確認"


class FinalResult(str, Enum):
    """最終結果"""
    OK = "OK"
    NEED_CONTROL = "要管制"


class DepartureRecord(BaseModel):
    """出発/起床記録モデル"""
    date: str = Field(..., description="日付（YYYY-MM-DD形式）")
    name: str = Field(..., max_length=100, description="氏名")
    line_id: str = Field(..., max_length=100, description="LINE ID")

    # 出発予定時間関連
    scheduled_departure_time: Optional[time] = Field(None, description="出発予定時間")
    actual_departure_time: Optional[datetime] = Field(None, description="出発報告時刻")
    departure_status: Optional[DepartureStatus] = Field(None, description="出発判定")
    departure_phone_call_count: int = Field(0, description="出発電話発信回数")

    # 起床予定時間関連
    scheduled_wakeup_time: Optional[time] = Field(None, description="起床予定時間")
    actual_wakeup_time: Optional[datetime] = Field(None, description="起床報告時刻")
    wakeup_status: Optional[WakeupStatus] = Field(None, description="起床判定")
    wakeup_phone_call_count: int = Field(0, description="起床電話発信回数")

    final_result: Optional[FinalResult] = Field(None, description="最終結果")
