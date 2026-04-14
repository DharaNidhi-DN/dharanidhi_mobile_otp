import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from mobile_otp.dao.base import BaseDao
from mobile_otp.models.otp import OtpEvent, OtpEventType, OtpStatus

logger = logging.getLogger(__name__)


class OtpEventDao(BaseDao[OtpEvent]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, OtpEvent)

    def create_event(
        self,
        otp_request_id: int,
        event_type: OtpEventType,
        status: OtpStatus,
        detail_json: dict[str, Any] | None = None
    ) -> OtpEvent:
        event = OtpEvent(
            otp_request_id=otp_request_id,
            event_type=event_type,
            status=status,
            detail_json=detail_json
        )
        logger.debug(
            "otp_event_created",
            extra={
                "otp_request_id": otp_request_id,
                "event_type": event_type.value,
                "status": status.value,
            }
        )
        self.add(event)
        return event
