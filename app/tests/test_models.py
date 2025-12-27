from datetime import time

import pytest

from app.models import Cast, DepartureRecord, DepartureStatus
from app.utils.validators import parse_time_string, validate_time_string


def test_validate_time_string():
    assert validate_time_string("08:30")
    assert not validate_time_string("08:33")


def test_parse_time_string():
    assert parse_time_string("09:00") == time(9, 0)
    assert parse_time_string("09:02") is None


def test_cast_time_increment_validation():
    with pytest.raises(ValueError):
        Cast(
            name="A",
            line_id="user_1",
            phone_number="+819012345678",
            default_departure_time=time(9, 3),
        )


def test_departure_record_defaults():
    record = DepartureRecord(date="2024-01-01", name="A", line_id="user_1")
    assert record.phone_call_count == 0
    assert record.departure_status is None
