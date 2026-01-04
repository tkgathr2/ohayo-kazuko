"""サービスのテスト"""
from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from app.services.departure_service import judge_departure, judge_wakeup, should_start_phone_call
from app.models import DepartureStatus, WakeupStatus
from app.utils.error_handler import retry_sync, calculate_backoff


@pytest.fixture
def jst():
    """JSTタイムゾーン"""
    return ZoneInfo("Asia/Tokyo")


class TestJudgeDeparture:
    """出発判定のテスト"""

    def test_ok_before_scheduled_time(self, jst):
        """予定時間以前はOK"""
        scheduled = time(8, 30)
        actual = datetime(2024, 1, 1, 8, 29, 59, tzinfo=jst)
        result = judge_departure(scheduled, actual, jst)
        assert result == DepartureStatus.OK

    def test_ok_at_scheduled_time(self, jst):
        """予定時間ちょうどはOK"""
        scheduled = time(8, 30)
        actual = datetime(2024, 1, 1, 8, 30, 0, tzinfo=jst)
        result = judge_departure(scheduled, actual, jst)
        assert result == DepartureStatus.OK

    def test_delayed_within_5_minutes(self, jst):
        """予定時間から5分以内は遅れ返"""
        scheduled = time(8, 30)
        actual = datetime(2024, 1, 1, 8, 34, 59, tzinfo=jst)
        result = judge_departure(scheduled, actual, jst)
        assert result == DepartureStatus.DELAYED

    def test_need_check_after_5_minutes(self, jst):
        """予定時間から5分超過は要確認"""
        scheduled = time(8, 30)
        actual = datetime(2024, 1, 1, 8, 35, 1, tzinfo=jst)
        result = judge_departure(scheduled, actual, jst)
        assert result == DepartureStatus.NEED_CHECK

    def test_none_when_no_scheduled_time(self, jst):
        """予定時間がNoneの場合はNone"""
        actual = datetime(2024, 1, 1, 8, 30, 0, tzinfo=jst)
        result = judge_departure(None, actual, jst)
        assert result is None

    def test_none_when_no_actual_time(self, jst):
        """報告時刻がNoneの場合はNone"""
        scheduled = time(8, 30)
        result = judge_departure(scheduled, None, jst)
        assert result is None


class TestJudgeWakeup:
    """起床判定のテスト"""

    def test_ok_before_scheduled_time(self, jst):
        """予定時間以前はOK"""
        scheduled = time(7, 0)
        actual = datetime(2024, 1, 1, 6, 59, 59, tzinfo=jst)
        result = judge_wakeup(scheduled, actual, jst)
        assert result == WakeupStatus.OK

    def test_delayed_within_5_minutes(self, jst):
        """予定時間から5分以内は遅れ返"""
        scheduled = time(7, 0)
        actual = datetime(2024, 1, 1, 7, 3, 0, tzinfo=jst)
        result = judge_wakeup(scheduled, actual, jst)
        assert result == WakeupStatus.DELAYED

    def test_need_check_after_5_minutes(self, jst):
        """予定時間から5分超過は要確認"""
        scheduled = time(7, 0)
        actual = datetime(2024, 1, 1, 7, 6, 0, tzinfo=jst)
        result = judge_wakeup(scheduled, actual, jst)
        assert result == WakeupStatus.NEED_CHECK


class TestShouldStartPhoneCall:
    """電話発信判定のテスト"""

    def test_should_not_call_when_already_reported(self, jst):
        """報告済みの場合は電話不要"""
        actual = datetime(2024, 1, 1, 8, 30, 0, tzinfo=jst)
        scheduled = time(8, 30)
        current = datetime(2024, 1, 1, 8, 35, 0, tzinfo=jst)
        result = should_start_phone_call(actual, scheduled, current, jst)
        assert result is False

    def test_should_call_when_overdue(self, jst):
        """予定時間を過ぎて未報告の場合は電話必要"""
        scheduled = time(8, 30)
        current = datetime(2024, 1, 1, 8, 31, 0, tzinfo=jst)
        result = should_start_phone_call(None, scheduled, current, jst)
        assert result is True

    def test_should_not_call_before_scheduled_time(self, jst):
        """予定時間前は電話不要"""
        scheduled = time(8, 30)
        current = datetime(2024, 1, 1, 8, 29, 0, tzinfo=jst)
        result = should_start_phone_call(None, scheduled, current, jst)
        assert result is False


class TestRetrySync:
    """リトライ機能のテスト"""

    def test_retry_on_failure(self, monkeypatch):
        """失敗時にリトライする"""
        calls = {"count": 0}

        def fail_then_succeed():
            calls["count"] += 1
            if calls["count"] < 2:
                raise ValueError("fail")
            return True

        monkeypatch.setattr("time.sleep", lambda _: None)
        result = retry_sync(
            fail_then_succeed,
            retryable_exceptions=[ValueError],
            retries=3,
            initial_backoff=0.0,
        )
        assert result is True
        assert calls["count"] == 2

    def test_max_retries_exceeded(self, monkeypatch):
        """最大リトライ回数を超えたらエラー"""
        calls = {"count": 0}

        def always_fail():
            calls["count"] += 1
            raise ValueError("always fail")

        monkeypatch.setattr("time.sleep", lambda _: None)
        with pytest.raises(Exception):
            retry_sync(
                always_fail,
                retryable_exceptions=[ValueError],
                retries=3,
                initial_backoff=0.0,
            )
        assert calls["count"] == 4  # 1 + 3 retries


class TestCalculateBackoff:
    """バックオフ計算のテスト"""

    def test_exponential_backoff(self):
        """指数バックオフが正しく計算される"""
        assert calculate_backoff(0, 1.0, 60.0) == 1.0
        assert calculate_backoff(1, 1.0, 60.0) == 2.0
        assert calculate_backoff(2, 1.0, 60.0) == 4.0
        assert calculate_backoff(3, 1.0, 60.0) == 8.0

    def test_max_backoff(self):
        """最大バックオフを超えない"""
        assert calculate_backoff(10, 1.0, 60.0) == 60.0
        assert calculate_backoff(100, 1.0, 60.0) == 60.0
