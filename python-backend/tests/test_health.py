import os
import unittest

from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://mobile_otp:mobile_otp@localhost:5432/mobile_otp"
)
os.environ.setdefault("TWILIO_ACCOUNT_SID", "test_account_sid")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "test_auth_token")
os.environ.setdefault("TWILIO_SERVICE_SID", "test_service_sid")

from mobile_otp import main as main_module  # noqa: E402


class HealthCheckTests(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        app = main_module.create_app()
        with TestClient(app) as client:
            response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
