import logging
from datetime import datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
logger.debug("schema_loaded", extra={"schema": "otp"})


class SendOtpRequest(BaseModel):
    phone_number: str = Field(min_length=6, max_length=32)
    channel: str = Field(default="sms")


class SendOtpResponse(BaseModel):
    request_id: int
    status: str
    twilio_sid: str | None
    channel: str
    to: str
    created_at: datetime
    expires_at: datetime | None


class VerifyOtpRequest(BaseModel):
    phone_number: str = Field(min_length=6, max_length=32)
    code: str = Field(min_length=4, max_length=10)


class VerifyOtpResponse(BaseModel):
    request_id: int
    status: str
    valid: bool
    twilio_status: str | None
    verified_at: datetime
