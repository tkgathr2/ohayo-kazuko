"""モデルのテスト"""
from datetime import time

import pytest

from app.models import Cast, DepartureRecord, DepartureStatus, WakeupStatus, FinalResult
from app.utils.validators import parse_time_string, validate_time_string


def test_validate_time_string():
    """時間文字列のバリデーション"""
    assert validate_time_string("08:30")
    assert validate_time_string("08:00")
    assert validate_time_string("08:35")
    assert not validate_time_string("08:33")
    assert not validate_time_string("08:31")
    assert not validate_time_string("invalid")


def test_parse_time_string():
    """時間文字列のパース"""
    assert parse_time_string("09:00") == time(9, 0)
    assert parse_time_string("09:30") == time(9, 30)
    assert parse_time_string("09:02") is None
    assert parse_time_string("invalid") is None


def test_cast_time_increment_validation():
    """キャストの時間が5分単位であることを検証"""
    # 正常なケース
    cast = Cast(
        name="テスト太郎",
        line_id="U1234567890abcdef1234567890abcdef",
        phone_number="+819012345678",
        default_departure_time=time(9, 0),
        default_wakeup_time=time(7, 30),
    )
    assert cast.default_departure_time == time(9, 0)
    assert cast.default_wakeup_time == time(7, 30)

    # 5分単位でない場合はエラー
    with pytest.raises(ValueError):
        Cast(
            name="A",
            line_id="U1234567890abcdef1234567890abcdef",
            phone_number="+819012345678",
            default_departure_time=time(9, 3),
        )

    with pytest.raises(ValueError):
        Cast(
            name="A",
            line_id="U1234567890abcdef1234567890abcdef",
            phone_number="+819012345678",
            default_wakeup_time=time(7, 33),
        )


def test_cast_wakeup_settings():
    """キャストの起床設定"""
    # デフォルトでは起床設定はOFF
    cast = Cast(
        name="テスト太郎",
        line_id="U1234567890abcdef1234567890abcdef",
        phone_number="+819012345678",
    )
    assert cast.wakeup_time_registration_enabled is False
    assert cast.default_wakeup_time is None
    assert cast.wakeup_offset_minutes == 0

    # 起床設定をONにする
    cast_with_wakeup = Cast(
        name="テスト太郎",
        line_id="U1234567890abcdef1234567890abcdef",
        phone_number="+819012345678",
        wakeup_time_registration_enabled=True,
        default_wakeup_time=time(7, 0),
        wakeup_offset_minutes=30,
    )
    assert cast_with_wakeup.wakeup_time_registration_enabled is True
    assert cast_with_wakeup.default_wakeup_time == time(7, 0)
    assert cast_with_wakeup.wakeup_offset_minutes == 30


def test_departure_record_defaults():
    """出発記録のデフォルト値"""
    record = DepartureRecord(
        date="2024-01-01",
        name="テスト太郎",
        line_id="U1234567890abcdef1234567890abcdef",
    )
    assert record.departure_phone_call_count == 0
    assert record.wakeup_phone_call_count == 0
    assert record.departure_status is None
    assert record.wakeup_status is None
    assert record.scheduled_departure_time is None
    assert record.scheduled_wakeup_time is None
    assert record.actual_departure_time is None
    assert record.actual_wakeup_time is None
    assert record.final_result is None


def test_departure_status_values():
    """出発ステータスの値"""
    assert DepartureStatus.OK.value == "OK"
    assert DepartureStatus.DELAYED.value == "遅れ返"
    assert DepartureStatus.NEED_CHECK.value == "要確認"


def test_wakeup_status_values():
    """起床ステータスの値"""
    assert WakeupStatus.OK.value == "OK"
    assert WakeupStatus.DELAYED.value == "遅れ返"
    assert WakeupStatus.NEED_CHECK.value == "要確認"


def test_final_result_values():
    """最終結果の値"""
    assert FinalResult.OK.value == "OK"
    assert FinalResult.NEED_CONTROL.value == "要管制"
