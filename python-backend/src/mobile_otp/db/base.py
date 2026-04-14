import logging

from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


logger.debug("sqlalchemy_base_ready")
