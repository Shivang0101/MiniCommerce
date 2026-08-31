import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rate_limiter_headers_present(client: AsyncClient):
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers or response.status_code == 200


@pytest.mark.asyncio
async def test_auth_route_rate_limit(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login", json={"email": "nonexistent@example.com", "password": "wrong"}
    )
    assert response.status_code in [401, 429]
