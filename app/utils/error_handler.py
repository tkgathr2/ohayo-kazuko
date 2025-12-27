import asyncio
import time
from typing import Any, Callable, Iterable, Optional, Type


class RetryableError(Exception):
    pass


def should_retry_status(status_code: int, retryable: Iterable[int]) -> bool:
    return status_code in retryable


async def retry_async(
    func: Callable[[], Any],
    retryable_exceptions: Optional[Iterable[Type[Exception]]] = None,
    retries: int = 3,
    backoff: float = 1.0,
) -> Any:
    retryable_exceptions = tuple(retryable_exceptions or ())
    attempt = 0
    while True:
        try:
            return await func()
        except retryable_exceptions as exc:
            attempt += 1
            if attempt > retries:
                raise
            await asyncio.sleep(backoff)
            backoff *= 2


def retry_sync(
    func: Callable[[], Any],
    retryable_exceptions: Optional[Iterable[Type[Exception]]] = None,
    retries: int = 3,
    backoff: float = 1.0,
) -> Any:
    retryable_exceptions = tuple(retryable_exceptions or ())
    attempt = 0
    while True:
        try:
            return func()
        except retryable_exceptions as exc:
            attempt += 1
            if attempt > retries:
                raise
            time.sleep(backoff)
            backoff *= 2
