import logging
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mobile_otp.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True
)

parsed = urlparse(settings.database_url)
logger.debug(
    "db_engine_initialized",
    extra={
        "db_host": parsed.hostname or "unknown",
        "db_port": parsed.port or 5432,
        "db_name": parsed.path.lstrip("/") if parsed.path else None,
    }
)

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)
