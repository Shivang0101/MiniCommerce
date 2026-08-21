import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_metrics_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/admin/metrics")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_admin_metrics_forbidden_for_regular_user(client: AsyncClient):
    email = "regular_user_test@example.com"
    await client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!"})
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/admin/metrics", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin privileges required"
