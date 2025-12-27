from datetime import datetime
from typing import Optional

from app.models import DepartureStatus


def judge_departure(
    actual_time: Optional[datetime],
    scheduled_time: datetime,
    current_time: datetime,
) -> Optional[DepartureStatus]:
    if actual_time is None:
        if current_time > scheduled_time:
            return DepartureStatus.NEED_CHECK
        return None

    actual_seconds = actual_time.replace(microsecond=0)
    scheduled_seconds = scheduled_time.replace(microsecond=0)
    if actual_seconds <= scheduled_seconds:
        return DepartureStatus.OK
    return DepartureStatus.DELAYED


def should_start_phone_call(
    actual_time: Optional[datetime],
    scheduled_time: datetime,
    current_time: datetime,
) -> bool:
    return actual_time is None and current_time > scheduled_time
