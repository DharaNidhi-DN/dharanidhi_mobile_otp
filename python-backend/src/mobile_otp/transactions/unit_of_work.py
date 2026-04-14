import logging
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession

from mobile_otp.db.session import SessionLocal

logger = logging.getLogger(__name__)


class UnitOfWork(AbstractAsyncContextManager):
    def __init__(self, session_factory: Callable[[], AsyncSession] = SessionLocal):
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        logger.debug("uow_session_started")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if not self.session:
            return
        if exc_type:
            logger.warning("uow_session_rollback", extra={"error": str(exc_value)})
            await self.session.rollback()
        else:
            logger.debug("uow_session_commit")
            await self.session.commit()
        await self.session.close()
        logger.debug("uow_session_closed")
