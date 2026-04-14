from __future__ import annotations

import logging
from typing import Generic, Iterable, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mobile_otp.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)
logger = logging.getLogger(__name__)


class BaseDao(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]):
        self.session = session
        self.model = model

    async def get(self, entity_id: int) -> ModelT | None:
        logger.debug(
            "dao_get",
            extra={"model": self.model.__name__, "entity_id": entity_id}
        )
        return await self.session.get(self.model, entity_id)

    def add(self, entity: ModelT) -> ModelT:
        logger.debug("dao_add", extra={"model": self.model.__name__})
        self.session.add(entity)
        return entity

    async def list(self, limit: int | None = None) -> Iterable[ModelT]:
        logger.debug(
            "dao_list",
            extra={"model": self.model.__name__, "limit": limit}
        )
        stmt = select(self.model)
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.scalars(stmt)
        return result.all()

    async def delete(self, entity: ModelT) -> None:
        logger.debug("dao_delete", extra={"model": self.model.__name__})
        await self.session.delete(entity)
