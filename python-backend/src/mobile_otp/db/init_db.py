import asyncio
import logging
from pathlib import Path

import anyio
from alembic import command
from alembic.config import Config

from mobile_otp.models import otp  # noqa: F401

logger = logging.getLogger(__name__)


async def init_db() -> None:
    base_dir = Path(__file__).resolve().parents[3]
    alembic_ini = base_dir / "alembic.ini"

    def _run_upgrade() -> None:
        logger.info("db_migration_start", extra={"alembic_ini": str(alembic_ini)})
        config = Config(str(alembic_ini))
        config.set_main_option("script_location", str(base_dir / "alembic"))
        command.upgrade(config, "head")
        logger.info("db_migration_complete")

    try:
        await anyio.to_thread.run_sync(_run_upgrade)
    except Exception:
        logger.exception("db_migration_failed")
        raise


if __name__ == "__main__":
    asyncio.run(init_db())
