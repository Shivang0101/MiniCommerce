from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Handle sqlite / postgresql URL compatibility
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("sqlite://") and not db_url.startswith("sqlite+aiosqlite://"):
    db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

# Configure connect_args for PgBouncer pooler compatibility (disables prepared statement caching)
connect_args = {}
if "asyncpg" in db_url:
    connect_args = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0
    }

engine_kwargs = {
    "echo": False,
    "future": True,
    "connect_args": connect_args
}
if "sqlite" not in db_url:
    engine_kwargs.update({
        "pool_size": 15,
        "max_overflow": 10,
        "pool_recycle": 1800,
        "pool_pre_ping": True
    })

engine = create_async_engine(db_url, **engine_kwargs)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
