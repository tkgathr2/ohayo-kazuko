from datetime import datetime

import pytest

from app.services.departure_service import judge_departure
from app.models import DepartureStatus
from app.utils.error_handler import retry_sync


def test_judge_departure_ok():
    scheduled = datetime(2024, 1, 1, 8, 30, 0)
    actual = datetime(2024, 1, 1, 8, 29, 59, 999999)
    result = judge_departure(actual, scheduled, actual)
    assert result == DepartureStatus.OK


def test_judge_departure_delayed():
    scheduled = datetime(2024, 1, 1, 8, 30, 0)
    actual = datetime(2024, 1, 1, 8, 30, 1)
    result = judge_departure(actual, scheduled, actual)
    assert result == DepartureStatus.DELAYED


def test_judge_departure_need_check():
    scheduled = datetime(2024, 1, 1, 8, 30, 0)
    now = datetime(2024, 1, 1, 8, 30, 1)
    result = judge_departure(None, scheduled, now)
    assert result == DepartureStatus.NEED_CHECK


def test_retry_sync_retries(monkeypatch):
    calls = {"count": 0}

    def fail_then_succeed():
        calls["count"] += 1
        if calls["count"] < 2:
            raise ValueError("fail")
        return True

    monkeypatch.setattr("time.sleep", lambda _: None)
    assert retry_sync(fail_then_succeed, retryable_exceptions=[ValueError], retries=2, backoff=0.0) is True
    assert calls["count"] == 2
