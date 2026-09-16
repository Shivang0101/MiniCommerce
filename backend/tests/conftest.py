import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from app.api.deps import get_db, get_read_db, get_write_db
from app.db.base import Base
from app.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:"),
)

connect_args = {}
pool_class = None
if "asyncpg" in TEST_DATABASE_URL:
    connect_args = {"statement_cache_size": 0, "prepared_statement_cache_size": 0}
    pool_class = NullPool

engine_kwargs = {"echo": False, "future": True, "connect_args": connect_args}
if pool_class:
    engine_kwargs["poolclass"] = pool_class

test_engine = create_async_engine(TEST_DATABASE_URL, **engine_kwargs)

TestSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_read_db] = _get_test_db
    app.dependency_overrides[get_write_db] = _get_test_db

    # Patch the production engine with the test engine to prevent lifespan
    # from creating a second conflicting asyncpg connection pool
    import app.db.session as session_module
    import app.main as main_module

    original_engine = main_module.engine
    session_module.engine = test_engine
    session_module.primary_engine = test_engine
    main_module.engine = test_engine

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Restore original engines
    session_module.engine = original_engine
    session_module.primary_engine = original_engine
    main_module.engine = original_engine
    app.dependency_overrides.clear()
