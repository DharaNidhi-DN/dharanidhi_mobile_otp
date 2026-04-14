from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mobile_otp.db.base import Base
from mobile_otp.utils.time import utc_now

logger = logging.getLogger(__name__)


class OtpStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELED = "canceled"


class OtpEventType(str, Enum):
    SEND_ATTEMPT = "send_attempt"
    VERIFY_ATTEMPT = "verify_attempt"
    STATUS_UPDATE = "status_update"


class OtpRequest(Base):
    __tablename__ = "otp_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_number: Mapped[str] = mapped_column(String(32), index=True)
    channel: Mapped[str] = mapped_column(String(16))
    status: Mapped[OtpStatus] = mapped_column(
        SqlEnum(OtpStatus, native_enum=False),
        default=OtpStatus.PENDING,
        index=True
    )
    twilio_verification_sid: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    twilio_service_sid: Mapped[str] = mapped_column(String(64))
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now
    )

    events: Mapped[list[OtpEvent]] = relationship(
        "OtpEvent",
        back_populates="otp_request",
        cascade="all, delete-orphan"
    )


class OtpEvent(Base):
    __tablename__ = "otp_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    otp_request_id: Mapped[int] = mapped_column(ForeignKey("otp_requests.id"), index=True)
    event_type: Mapped[OtpEventType] = mapped_column(SqlEnum(OtpEventType, native_enum=False))
    status: Mapped[OtpStatus] = mapped_column(SqlEnum(OtpStatus, native_enum=False))
    detail_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    otp_request: Mapped[OtpRequest] = relationship("OtpRequest", back_populates="events")


logger.debug("models_loaded", extra={"model": "otp"})
