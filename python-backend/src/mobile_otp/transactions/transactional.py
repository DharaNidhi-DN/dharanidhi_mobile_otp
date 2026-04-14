from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from mobile_otp.db.session import SessionLocal

P = ParamSpec("P")
R = TypeVar("R")
logger = logging.getLogger(__name__)


def transactional(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        session: AsyncSession | None = kwargs.get("session")
        if session is not None:
            logger.debug("transaction_reuse_session")
            return await func(*args, **kwargs)

        async with SessionLocal() as session:
            try:
                kwargs["session"] = session
                result = await func(*args, **kwargs)
                await session.commit()
                logger.debug("transaction_commit", extra={"func": func.__name__})
                return result
            except Exception:
                await session.rollback()
                logger.warning("transaction_rollback", extra={"func": func.__name__})
                raise

    return wrapper
