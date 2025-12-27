import re
from datetime import time
from typing import Optional

PHONE_NUMBER_PATTERN = r'^\+[1-9]\d{1,14}$'
TIME_PATTERN = r'^([0-1]?[0-9]|2[0-3]):([0-5][05])$'
DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'
LINE_ID_PATTERN = r'^[a-zA-Z0-9_]+$'


def validate_time_string(value: str) -> bool:
    return re.match(TIME_PATTERN, value) is not None


def parse_time_string(value: str) -> Optional[time]:
    if not validate_time_string(value):
        return None
    hour, minute = value.split(":")
    return time(int(hour), int(minute))