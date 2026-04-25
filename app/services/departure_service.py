"""出発/起床判定サービス"""
from datetime import datetime, time
from typing import Optional

from zoneinfo import ZoneInfo

from app.models import DepartureStatus, WakeupStatus


def judge_departure(
    scheduled_time: Optional[time],
    actual_time: Optional[datetime],
    tz: Optional[ZoneInfo] = None,
) -> Optional[DepartureStatus]:
    """
    出発判定ロジック

    判定は出発報告ボタン押下時刻のみを使用

    Args:
        scheduled_time: 出発予定時間（time型）
        actual_time: 出発報告時刻（datetime型）
        tz: タイムゾーン

    Returns:
        判定結果
    """
    if scheduled_time is None or actual_time is None:
        return None

    # タイムゾーンを確保
    if tz is None:
        tz = ZoneInfo("Asia/Tokyo")

    # actual_timeにタイムゾーンがない場合は付与
    if actual_time.tzinfo is None:
        actual_time = actual_time.replace(tzinfo=tz)
    else:
        actual_time = actual_time.astimezone(tz)

    # 予定時間をdatetimeに変換
    scheduled_datetime = datetime.combine(
        actual_time.date(),
        scheduled_time,
        tzinfo=tz
    )

    # 差分を計算（分単位）
    diff_seconds = (actual_time - scheduled_datetime).total_seconds()
    diff_minutes = diff_seconds / 60

    # 判定
    # 予定時間以前: OK
    # 予定時間～5分以内: 遅れ返
    # 5分超過: 要確認
    if diff_minutes <= 0:
        return DepartureStatus.OK
    elif diff_minutes <= 5:
        return DepartureStatus.DELAYED
    else:
        return DepartureStatus.NEED_CHECK


def judge_wakeup(
    scheduled_time: Optional[time],
    actual_time: Optional[datetime],
    tz: Optional[ZoneInfo] = None,
) -> Optional[WakeupStatus]:
    """
    起床判定ロジック（出発判定と同じ）

    判定は起床報告ボタン押下時刻のみを使用

    Args:
        scheduled_time: 起床予定時間（time型）
        actual_time: 起床報告時刻（datetime型）
        tz: タイムゾーン

    Returns:
        判定結果
    """
    result = judge_departure(scheduled_time, actual_time, tz)
    if result is None:
        return None
    return WakeupStatus(result.value)


def should_start_phone_call(
    actual_time: Optional[datetime],
    scheduled_time: time,
    current_time: datetime,
    tz: Optional[ZoneInfo] = None,
) -> bool:
    """
    電話発信を開始すべきか判定

    Args:
        actual_time: 報告時刻（None = 未報告）
        scheduled_time: 予定時間
        current_time: 現在時刻
        tz: タイムゾーン

    Returns:
        電話発信すべき場合True
    """
    if actual_time is not None:
        return False

    if tz is None:
        tz = ZoneInfo("Asia/Tokyo")

    # 現在時刻にタイムゾーンがない場合は付与
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=tz)

    scheduled_datetime = datetime.combine(
        current_time.date(),
        scheduled_time,
        tzinfo=tz
    )

    return current_time > scheduled_datetime
