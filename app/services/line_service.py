import base64
import hashlib
import hmac
from typing import Optional

import httpx

from app.config import Settings
from app.utils.error_handler import retry_async
from app.utils.logger import get_logger


class LineService:
    def __init__(self, settings: Settings, client: Optional[httpx.AsyncClient] = None) -> None:
        self._settings = settings
        self._client = client or httpx.AsyncClient(timeout=30.0)
        self._logger = get_logger("line_service")

    def verify_signature(self, body: bytes, signature: str) -> bool:
        secret = self._settings.line_channel_secret.get_secret_value().encode("utf-8")
        digest = hmac.new(secret, body, hashlib.sha256).digest()
        expected = base64.b64encode(digest).decode("utf-8")
        return hmac.compare_digest(expected, signature)

    async def send_message(self, line_id: str, message: str) -> bool:
        payload = {
            "to": line_id,
            "messages": [{"type": "text", "text": message}],
        }
        return await self._post_with_retry(payload)

    async def send_notification(self, line_id: str, notification: dict) -> bool:
        payload = {"to": line_id, "messages": [notification]}
        return await self._post_with_retry(payload)

    async def _post_with_retry(self, payload: dict) -> bool:
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Authorization": f"Bearer {self._settings.line_channel_access_token.get_secret_value()}",
            "Content-Type": "application/json",
        }

        async def send() -> bool:
            resp = await self._client.post(url, json=payload, headers=headers)
            if resp.status_code in (401, 403):
                self._logger.error("LINE auth error status=%s", resp.status_code)
                return False
            if resp.status_code in (400,):
                self._logger.warning("LINE bad request status=%s body=%s", resp.status_code, resp.text)
                return False
            if resp.status_code in (429, 500, 502, 503, 504):
                raise httpx.HTTPStatusError("retryable", request=resp.request, response=resp)
            if resp.is_error:
                self._logger.error("LINE error status=%s body=%s", resp.status_code, resp.text)
                return False
            return True

        try:
            return await retry_async(
                send,
                retryable_exceptions=[httpx.HTTPStatusError, httpx.TimeoutException],
                retries=5,
                initial_backoff=1.0,
            )
        except Exception as exc:
            self._logger.error("LINE send failed: %s", exc)
            return False

    async def close(self) -> None:
        await self._client.aclose()
