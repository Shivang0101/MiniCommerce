import pytest
from app.core.config import Settings
from app.db.session import _format_db_url, get_db, get_read_db, get_write_db
from sqlalchemy.ext.asyncio import AsyncSession


def test_format_db_url():
    pg_url = _format_db_url("postgresql://user:pass@localhost:5432/db")
    assert pg_url.startswith("postgresql+asyncpg://")

    sqlite_url = _format_db_url("sqlite:///./test.db")
    assert sqlite_url.startswith("sqlite+aiosqlite://")


@pytest.mark.asyncio
async def test_get_write_and_read_db_generators(db_session: AsyncSession):
    # Verify get_write_db yields a valid AsyncSession
    async for session in get_write_db():
        assert isinstance(session, AsyncSession)
        break

    # Verify get_db yields a valid AsyncSession
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        break

    # Verify get_read_db yields a valid AsyncSession (with fallback)
    async for session in get_read_db():
        assert isinstance(session, AsyncSession)
        break


def test_settings_read_database_url_default():
    s = Settings()
    assert s.READ_DATABASE_URL is None
