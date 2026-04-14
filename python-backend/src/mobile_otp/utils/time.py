import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    now = datetime.now(timezone.utc)
    logger.debug("utc_now_called", extra={"iso": now.isoformat()})
    return now


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        logger.debug("ensure_utc_assumed", extra={"value": value.isoformat()})
        return value.replace(tzinfo=timezone.utc)
    converted = value.astimezone(timezone.utc)
    logger.debug("ensure_utc_converted", extra={"value": converted.isoformat()})
    return converted
