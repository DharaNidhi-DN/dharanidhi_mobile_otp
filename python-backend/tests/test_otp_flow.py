import os
import unittest
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://mobile_otp:mobile_otp@localhost:5432/mobile_otp"
)
os.environ.setdefault("TWILIO_ACCOUNT_SID", "test_account_sid")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "test_auth_token")
os.environ.setdefault("TWILIO_SERVICE_SID", "test_service_sid")

from mobile_otp import main as main_module  # noqa: E402


class FakeTwilioVerifyClient:
    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        service_sid: str,
        base_url: str = "https://verify.twilio.com/v2",
        timeout: float = 10.0
    ) -> None:
        self._service_sid = service_sid

    @property
    def service_sid(self) -> str:
        return self._service_sid

    async def close(self) -> None:
        return None

    async def send_otp(self, to: str, channel: str) -> dict[str, str]:
        return {
            "sid": f"VA_TEST_{uuid.uuid4().hex}",
            "status": "pending",
            "to": to,
            "channel": channel
        }

    async def verify_otp(self, to: str, code: str) -> dict[str, object]:
        return {"status": "approved", "valid": True}


class OtpFlowTests(unittest.TestCase):
    def test_send_and_verify_otp(self) -> None:
        phone_number = "+15551234567"
        payload = {"phone_number": phone_number, "channel": "sms"}

        with patch.object(main_module, "TwilioVerifyClient", FakeTwilioVerifyClient):
            app = main_module.create_app()
            with TestClient(app) as client:
                send_response = client.post("/otp/send", json=payload)
                self.assertEqual(send_response.status_code, 200)
                send_data = send_response.json()
                self.assertEqual(send_data["to"], phone_number)
                self.assertEqual(send_data["status"], "pending")

                verify_response = client.post(
                    "/otp/verify",
                    json={"phone_number": phone_number, "code": "123456"}
                )
                self.assertEqual(verify_response.status_code, 200)
                verify_data = verify_response.json()
                self.assertTrue(verify_data["valid"])
