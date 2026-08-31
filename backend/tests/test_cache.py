from unittest.mock import AsyncMock, patch

import pytest
from app.main import app
from app.services.cache_service import CacheService
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_liveness_probe():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "minicommerce-backend"


@pytest.mark.asyncio
async def test_readiness_probe_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/readyz")
        # In test mode without active redis/db, verify structure
        assert response.status_code in [200, 503]
        data = response.json()
        assert "dependencies" in data
        assert "database" in data["dependencies"]
        assert "redis" in data["dependencies"]


@pytest.mark.asyncio
async def test_cache_service_fallback_when_redis_none():
    with patch("app.services.cache_service.get_redis", return_value=None):
        val = await CacheService.get("test_key")
        assert val is None

        set_res = await CacheService.set("test_key", {"foo": "bar"})
        assert set_res is False

        inv_res = await CacheService.invalidate_pattern("products:*")
        assert inv_res == 0


@pytest.mark.asyncio
async def test_cache_service_get_set_mocked():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '{"products": [], "total_count": 0}'
    mock_redis.setex.return_value = True

    with patch("app.services.cache_service.get_redis", return_value=mock_redis):
        data = await CacheService.get("products:page=1")
        assert data == {"products": [], "total_count": 0}

        success = await CacheService.set("products:page=1", {"products": [], "total_count": 0})
        assert success is True


@pytest.mark.asyncio
async def test_cache_service_handles_redis_error():
    mock_redis = AsyncMock()
    mock_redis.get.side_effect = Exception("Redis connection refused")

    with patch("app.services.cache_service.get_redis", return_value=mock_redis):
        data = await CacheService.get("products:page=1")
        # Should gracefully return None instead of raising exception
        assert data is None
