import logging
from datetime import timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from mobile_otp.core.config import Settings
from mobile_otp.core.errors import OtpExpiredError, OtpRequestNotFoundError
from mobile_otp.dao.otp_event_dao import OtpEventDao
from mobile_otp.dao.otp_request_dao import OtpRequestDao
from mobile_otp.integrations.twilio_verify_client import TwilioVerifyClient
from mobile_otp.models.otp import OtpEventType, OtpRequest, OtpStatus
from mobile_otp.transactions.transactional import transactional
from mobile_otp.transactions.unit_of_work import UnitOfWork
from mobile_otp.utils.time import ensure_utc, utc_now
from mobile_otp.utils.redaction import mask_phone

logger = logging.getLogger(__name__)


class OtpService:
    def __init__(
        self,
        client: TwilioVerifyClient,
        settings: Settings,
        session_factory
    ) -> None:
        self._client = client
        self._settings = settings
        self._session_factory = session_factory

    async def send_otp(self, phone_number: str, channel: str = "sms") -> OtpRequest:
        logger.info(
            "otp_send_start",
            extra={"phone": mask_phone(phone_number), "channel": channel}
        )
        expires_at = utc_now() + timedelta(seconds=self._settings.otp_expiry_seconds)

        async with UnitOfWork(self._session_factory) as uow:
            request = OtpRequest(
                phone_number=phone_number,
                channel=channel,
                status=OtpStatus.PENDING,
                twilio_service_sid=self._client.service_sid,
                expires_at=expires_at
            )
            OtpRequestDao(uow.session).add(request)
            await uow.session.flush()

            response = await self._client.send_otp(phone_number, channel)
            request.twilio_verification_sid = response.get("sid")
            request.status = OtpStatus.PENDING
            request.attempt_count += 1

            OtpEventDao(uow.session).create_event(
                otp_request_id=request.id,
                event_type=OtpEventType.SEND_ATTEMPT,
                status=OtpStatus.PENDING,
                detail_json=response
            )

            logger.info(
                "otp_send_complete",
                extra={
                    "request_id": request.id,
                    "status": request.status.value,
                    "attempt_count": request.attempt_count,
                },
            )
            return request

    @transactional
    async def verify_otp(
        self,
        phone_number: str,
        code: str,
        *,
        session: AsyncSession
    ) -> tuple[OtpRequest, dict[str, Any]]:
        request_dao = OtpRequestDao(session)
        event_dao = OtpEventDao(session)

        request = await request_dao.get_latest_by_phone(phone_number)
        if not request:
            logger.warning(
                "otp_verify_missing_request",
                extra={"phone": mask_phone(phone_number)}
            )
            raise OtpRequestNotFoundError("No OTP request found for this phone number")

        if request.expires_at:
            expires_at = ensure_utc(request.expires_at)
            if utc_now() > expires_at:
                request.status = OtpStatus.EXPIRED
                event_dao.create_event(
                    otp_request_id=request.id,
                    event_type=OtpEventType.STATUS_UPDATE,
                    status=OtpStatus.EXPIRED,
                    detail_json={"reason": "expired"}
                )
                logger.info(
                    "otp_verify_expired",
                    extra={"request_id": request.id, "status": request.status.value}
                )
                raise OtpExpiredError("OTP has expired")

        response = await self._client.verify_otp(phone_number, code)
        is_approved = response.get("status") == "approved" and response.get("valid") is True
        request.status = OtpStatus.APPROVED if is_approved else OtpStatus.FAILED
        request.attempt_count += 1

        event_dao.create_event(
            otp_request_id=request.id,
            event_type=OtpEventType.VERIFY_ATTEMPT,
            status=request.status,
            detail_json=response
        )

        logger.info(
            "otp_verify_complete",
            extra={
                "request_id": request.id,
                "status": request.status.value,
                "approved": request.status == OtpStatus.APPROVED,
            },
        )
        return request, response
