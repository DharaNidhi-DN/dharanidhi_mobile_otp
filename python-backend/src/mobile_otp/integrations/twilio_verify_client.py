import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class TwilioVerifyClient:
    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        service_sid: str,
        base_url: str = "https://verify.twilio.com/v2",
        timeout: float = 10.0
    ) -> None:
        self._service_sid = service_sid
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            auth=(account_sid, auth_token)
        )

    @property
    def service_sid(self) -> str:
        return self._service_sid

    async def close(self) -> None:
        await self._client.aclose()

    async def send_otp(self, to: str, channel: str) -> dict[str, Any]:
        return await self._post(
            path=f"/Services/{self._service_sid}/Verifications",
            payload={"To": to, "Channel": channel},
            action="send_otp",
        )

    async def verify_otp(self, to: str, code: str) -> dict[str, Any]:
        return await self._post(
            path=f"/Services/{self._service_sid}/VerificationCheck",
            payload={"To": to, "Code": code},
            action="verify_otp",
        )

    async def _post(
        self,
        *,
        path: str,
        payload: dict[str, Any],
        action: str,
    ) -> dict[str, Any]:
        try:
            response = await self._client.post(path, data=payload)
            response.raise_for_status()
            logger.info(
                "twilio_request_success",
                extra={"action": action, "status_code": response.status_code}
            )
            return response.json()
        except httpx.HTTPStatusError as exc:
            error_code = None
            try:
                data = exc.response.json()
                error_code = data.get("code")
            except Exception:
                pass
            logger.warning(
                "twilio_request_failed",
                extra={
                    "action": action,
                    "status_code": exc.response.status_code,
                    "twilio_error_code": error_code,
                },
            )
            raise
        except httpx.HTTPError:
            logger.exception("twilio_request_error", extra={"action": action})
            raise
