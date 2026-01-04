"""エラーハンドリング（指数バックオフ対応）"""
import asyncio
import time
from datetime import datetime
from typing import Any, Callable, Iterable, Optional, Type

from app.utils.logger import get_logger

logger = get_logger("error_handler")

# 最大リトライ回数
MAX_RETRIES = 5

# 初期バックオフ時間（秒）
INITIAL_BACKOFF = 1.0

# 最大バックオフ時間（秒）
MAX_BACKOFF = 60.0


class RetryableError(Exception):
    """リトライ可能なエラー"""
    pass


class MaxRetriesExceededError(Exception):
    """最大リトライ回数超過エラー"""
    def __init__(self, message: str, original_exception: Exception):
        super().__init__(message)
        self.original_exception = original_exception


def calculate_backoff(attempt: int, initial: float = INITIAL_BACKOFF, max_backoff: float = MAX_BACKOFF) -> float:
    """指数バックオフを計算"""
    backoff = initial * (2 ** attempt)
    return min(backoff, max_backoff)


def should_retry_status(status_code: int, retryable: Iterable[int]) -> bool:
    """リトライすべきHTTPステータスコードか判定"""
    return status_code in retryable


async def retry_async(
    func: Callable[[], Any],
    retryable_exceptions: Optional[Iterable[Type[Exception]]] = None,
    retries: int = MAX_RETRIES,
    initial_backoff: float = INITIAL_BACKOFF,
    max_backoff: float = MAX_BACKOFF,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
    on_failure: Optional[Callable[[Exception], Any]] = None,
) -> Any:
    """
    非同期関数を指数バックオフでリトライ

    Args:
        func: 実行する非同期関数
        retryable_exceptions: リトライ対象の例外クラス
        retries: 最大リトライ回数（デフォルト: 5）
        initial_backoff: 初期バックオフ時間（秒）
        max_backoff: 最大バックオフ時間（秒）
        on_retry: リトライ時に呼び出されるコールバック（attempt, exception）
        on_failure: 最終失敗時に呼び出されるコールバック（exception）

    Returns:
        関数の戻り値

    Raises:
        MaxRetriesExceededError: 最大リトライ回数超過時
    """
    retryable_exceptions = tuple(retryable_exceptions or ())
    attempt = 0
    last_exception = None

    while True:
        try:
            return await func()
        except retryable_exceptions as exc:
            last_exception = exc
            attempt += 1

            if attempt > retries:
                logger.error(
                    "Max retries exceeded after %d attempts: %s",
                    attempt - 1,
                    str(exc)
                )
                if on_failure:
                    await on_failure(exc) if asyncio.iscoroutinefunction(on_failure) else on_failure(exc)
                raise MaxRetriesExceededError(
                    f"Max retries ({retries}) exceeded",
                    exc
                )

            backoff = calculate_backoff(attempt - 1, initial_backoff, max_backoff)
            logger.warning(
                "Retry attempt %d/%d after %.1fs: %s",
                attempt,
                retries,
                backoff,
                str(exc)
            )

            if on_retry:
                on_retry(attempt, exc)

            await asyncio.sleep(backoff)


def retry_sync(
    func: Callable[[], Any],
    retryable_exceptions: Optional[Iterable[Type[Exception]]] = None,
    retries: int = MAX_RETRIES,
    initial_backoff: float = INITIAL_BACKOFF,
    max_backoff: float = MAX_BACKOFF,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
    on_failure: Optional[Callable[[Exception], None]] = None,
) -> Any:
    """
    同期関数を指数バックオフでリトライ

    Args:
        func: 実行する関数
        retryable_exceptions: リトライ対象の例外クラス
        retries: 最大リトライ回数（デフォルト: 5）
        initial_backoff: 初期バックオフ時間（秒）
        max_backoff: 最大バックオフ時間（秒）
        on_retry: リトライ時に呼び出されるコールバック（attempt, exception）
        on_failure: 最終失敗時に呼び出されるコールバック（exception）

    Returns:
        関数の戻り値

    Raises:
        MaxRetriesExceededError: 最大リトライ回数超過時
    """
    retryable_exceptions = tuple(retryable_exceptions or ())
    attempt = 0

    while True:
        try:
            return func()
        except retryable_exceptions as exc:
            attempt += 1

            if attempt > retries:
                logger.error(
                    "Max retries exceeded after %d attempts: %s",
                    attempt - 1,
                    str(exc)
                )
                if on_failure:
                    on_failure(exc)
                raise MaxRetriesExceededError(
                    f"Max retries ({retries}) exceeded",
                    exc
                )

            backoff = calculate_backoff(attempt - 1, initial_backoff, max_backoff)
            logger.warning(
                "Retry attempt %d/%d after %.1fs: %s",
                attempt,
                retries,
                backoff,
                str(exc)
            )

            if on_retry:
                on_retry(attempt, exc)

            time.sleep(backoff)


def format_error_for_slack(
    error_type: str,
    error_message: str,
    additional_info: Optional[dict] = None
) -> dict:
    """Slack通知用のエラーフォーマットを生成"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S JST")

    fields = [
        {"title": "エラータイプ", "value": error_type, "short": True},
        {"title": "発生時刻", "value": now, "short": True},
        {"title": "エラーメッセージ", "value": error_message, "short": False},
    ]

    if additional_info:
        for key, value in additional_info.items():
            fields.append({"title": key, "value": str(value), "short": True})

    return {
        "text": "エラーが発生しました",
        "attachments": [
            {
                "color": "danger",
                "title": "エラー詳細",
                "fields": fields
            }
        ]
    }
