import logging

logger = logging.getLogger(__name__)


class OtpRequestNotFoundError(Exception):
    pass


class OtpExpiredError(Exception):
    pass


logger.debug("error_types_loaded", extra={"module": "core.errors"})
