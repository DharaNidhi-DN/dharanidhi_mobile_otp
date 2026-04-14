from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def mask_phone(phone_number: str) -> str:
    if not phone_number:
        logger.debug("mask_phone_empty")
        return ""
    trimmed = phone_number.strip()
    if len(trimmed) <= 4:
        logger.debug("mask_phone_short", extra={"length": len(trimmed)})
        return "*" * len(trimmed)
    prefix = trimmed[:2]
    suffix = trimmed[-2:]
    masked = f"{prefix}{'*' * (len(trimmed) - 4)}{suffix}"
    logger.debug("mask_phone_applied", extra={"length": len(trimmed)})
    return masked
