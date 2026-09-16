import logging
from collections.abc import AsyncGenerator

from app.core.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)


def _format_db_url(raw_url: str) -> str:
    url = raw_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite://") and not url.startswith("sqlite+aiosqlite://"):
        url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return url


def _create_engine(url: str) -> AsyncEngine:
    formatted_url = _format_db_url(url)
    connect_args = {}
    if "asyncpg" in formatted_url:
        connect_args = {"statement_cache_size": 0, "prepared_statement_cache_size": 0}

    engine_kwargs = {"echo": False, "future": True, "connect_args": connect_args}
    if "sqlite" not in formatted_url:
        engine_kwargs.update(
            {
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_recycle": settings.DB_POOL_RECYCLE,
                "pool_pre_ping": True,
            }
        )
    return create_async_engine(formatted_url, **engine_kwargs)


# Primary (Master) Database Engine
primary_url = settings.DATABASE_URL
primary_engine = _create_engine(primary_url)
AsyncSessionPrimary = async_sessionmaker(
    bind=primary_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

# Backwards compatibility alias for single engine
engine = primary_engine
AsyncSessionLocal = AsyncSessionPrimary

# Read-Replica Database Engine
replica_url = settings.READ_DATABASE_URL
if replica_url:
    replica_engine = _create_engine(replica_url)
    AsyncSessionReplica = async_sessionmaker(
        bind=replica_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
else:
    replica_engine = primary_engine
    AsyncSessionReplica = AsyncSessionPrimary


async def get_write_db() -> AsyncGenerator[AsyncSession, None]:
    """Routes mutations (INSERT, UPDATE, DELETE, SELECT FOR UPDATE) to the primary database."""
    async with AsyncSessionPrimary() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Default database session generator (alias to get_write_db)."""
    async with AsyncSessionPrimary() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_read_db() -> AsyncGenerator[AsyncSession, None]:
    """Routes read-only queries to the read-replica database pool with primary fallback."""
    if replica_engine is primary_engine:
        async with AsyncSessionPrimary() as session:
            try:
                yield session
            finally:
                await session.close()
        return

    try:
        session = AsyncSessionReplica()
    except Exception as exc:
        logger.warning(
            "Read replica session creation failed (%s). Falling back to primary database.", exc
        )
        async with AsyncSessionPrimary() as fallback_session:
            try:
                yield fallback_session
            finally:
                await fallback_session.close()
        return

    async with session:
        try:
            yield session
        finally:
            await session.close()
