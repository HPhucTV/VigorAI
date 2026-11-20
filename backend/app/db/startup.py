# [OWNER: M3] Cloud Startup Runner: Alembic Migrations + Idempotent Seed (T-M3-06)
import asyncio
import logging
import subprocess
import sys
import time
from urllib.parse import urlsplit, urlunsplit

from app.core.config import settings
from app.db.seed_catalog_and_exercises import seed_catalog_and_exercises
from app.db.seed_demo_history import seed_demo_history
from app.db.session import AsyncSessionLocal, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("vigorai.startup")

MAX_MIGRATION_ATTEMPTS = 5
RETRY_BACKOFF_SECONDS = 3.0


def _mask_database_url(url: str) -> str:
    """An thong tin user/password khi ghi log DATABASE_URL."""
    try:
        parts = urlsplit(url)
        hostname = parts.hostname or "unknown-host"
        port_part = f":{parts.port}" if parts.port else ""
        netloc = f"***@{hostname}{port_part}" if parts.username or parts.password else f"{hostname}{port_part}"
        return urlunsplit((parts.scheme, netloc, parts.path, parts.query, ""))
    except Exception:
        return "<invalid-database-url>"


def _run_migrations_with_retry() -> bool:
    """Chay Alembic upgrade head voi co che retry tranh loi cold-start PostgreSQL."""
    for attempt in range(1, MAX_MIGRATION_ATTEMPTS + 1):
        logger.info(
            "Chay Alembic migration (lan %d/%d) toi %s",
            attempt,
            MAX_MIGRATION_ATTEMPTS,
            _mask_database_url(settings.DATABASE_URL),
        )
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=False,
        )
        if result.returncode == 0:
            logger.info("Alembic migration hoan tat thanh cong.")
            return True

        if attempt < MAX_MIGRATION_ATTEMPTS:
            logger.warning(
                "Alembic migration that bai (exit=%d). Thu lai sau %.0fs...",
                result.returncode,
                RETRY_BACKOFF_SECONDS,
            )
            time.sleep(RETRY_BACKOFF_SECONDS)

    logger.error(
        "Khong the ket noi PostgreSQL sau %d lan thu. "
        "Tren Railway: hay them PostgreSQL service vao Project -> "
        "vao Service Variables dat DATABASE_URL=${{Postgres.DATABASE_URL}}.",
        MAX_MIGRATION_ATTEMPTS,
    )
    return False


async def _run_seed() -> None:
    """Nap du lieu chuan (food catalog + 30 bai tap + 4 giao an mau + user demo) mot cach idempotent."""
    try:
        async with AsyncSessionLocal() as db:
            stats = await seed_catalog_and_exercises(db)
            logger.info("Idempotent seed hoan tat: %s", stats)
            demo_stats = await seed_demo_history(db)
            logger.info("Idempotent demo history seed hoan tat: %s", demo_stats)
    finally:
        await engine.dispose()


def main() -> int:
    if settings.RUN_MIGRATIONS_ON_STARTUP:
        if not _run_migrations_with_retry():
            return 1
    else:
        logger.info("Bo qua Alembic migration luc khoi dong (RUN_MIGRATIONS_ON_STARTUP=false).")

    if settings.RUN_SEED_ON_STARTUP:
        asyncio.run(_run_seed())
    else:
        logger.info("Bo qua seed luc khoi dong (RUN_SEED_ON_STARTUP=false).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
