import html
import json
from typing import Optional

import httpx

from app.config import Settings
from app.utils.error_handler import retry_async
from app.utils.logger import get_logger


class TwilioService:
    def __init__(self, settings: Settings, client: Optional[httpx.AsyncClient] = None) -> None:
        self._settings = settings
        self._client = client or httpx.AsyncClient(timeout=30.0)
        self._logger = get_logger("twilio_service")

    async def make_call(self, phone_number: str, message: str) -> Optional[str]:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self._settings.twilio_account_sid}/Calls.json"
        auth = (self._settings.twilio_account_sid, self._settings.twilio_auth_token.get_secret_value())
        twiml = f"<Response><Say language=\"ja-JP\">{html.escape(message)}</Say></Response>"
        data = {"To": phone_number, "From": self._settings.twilio_phone_number, "Twiml": twiml}

        async def send() -> httpx.Response:
            resp = await self._client.post(url, data=data, auth=auth)
            if resp.status_code in (429, 500, 502, 503, 504):
                raise httpx.HTTPStatusError("retryable", request=resp.request, response=resp)
            return resp

        try:
            resp = await retry_async(
                send,
                retryable_exceptions=[httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError],
                retries=3,
                initial_backoff=1.0,
            )
        except Exception as exc:
            self._logger.error("Twilio call failed: %s", exc)
            return None

        if resp.status_code >= 400:
            self._logger.error("Twilio error status=%s body=%s", resp.status_code, resp.text)
            return None
        payload = resp.json()
        return payload.get("sid")

    async def cancel_call(self, call_sid: str) -> bool:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self._settings.twilio_account_sid}/Calls/{call_sid}.json"
        auth = (self._settings.twilio_account_sid, self._settings.twilio_auth_token.get_secret_value())

        async def send() -> httpx.Response:
            resp = await self._client.post(url, data={"Status": "canceled"}, auth=auth)
            if resp.status_code in (429, 500, 502, 503, 504):
                raise httpx.HTTPStatusError("retryable", request=resp.request, response=resp)
            return resp

        try:
            resp = await retry_async(
                send,
                retryable_exceptions=[httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError],
                retries=3,
                initial_backoff=1.0,
            )
        except Exception as exc:
            self._logger.error("Twilio cancel failed: %s", exc)
            return False

        if resp.status_code >= 400:
            self._logger.error("Twilio cancel error status=%s body=%s", resp.status_code, resp.text)
            return False
        return True

    async def close(self) -> None:
        await self._client.aclose()
