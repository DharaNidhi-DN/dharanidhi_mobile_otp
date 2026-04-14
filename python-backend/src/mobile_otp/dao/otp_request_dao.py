import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mobile_otp.dao.base import BaseDao
from mobile_otp.models.otp import OtpRequest
from mobile_otp.utils.redaction import mask_phone

logger = logging.getLogger(__name__)


class OtpRequestDao(BaseDao[OtpRequest]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, OtpRequest)

    async def get_latest_by_phone(self, phone_number: str) -> OtpRequest | None:
        logger.debug(
            "otp_request_latest_lookup",
            extra={"phone": mask_phone(phone_number)}
        )
        stmt = (
            select(OtpRequest)
            .where(OtpRequest.phone_number == phone_number)
            .order_by(OtpRequest.created_at.desc())
            .limit(1)
        )
        result = await self.session.scalars(stmt)
        return result.first()

    async def get_by_twilio_sid(self, sid: str) -> OtpRequest | None:
        logger.debug("otp_request_sid_lookup")
        stmt = select(OtpRequest).where(OtpRequest.twilio_verification_sid == sid)
        result = await self.session.scalars(stmt)
        return result.first()
