import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "email": "testuser@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@example.com", "password": "Password123!"}
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "Password123!"
    })

    login_res = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "wrongpwd@example.com",
        "password": "Password123!"
    })

    login_res = await client.post("/api/v1/auth/login", json={
        "email": "wrongpwd@example.com",
        "password": "WrongPassword!"
    })
    assert login_res.status_code == 401

@pytest.mark.asyncio
async def test_me_and_invalid_token(client: AsyncClient):
    # Invalid token test
    invalid_me = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert invalid_me.status_code == 401

    # Valid token test
    await client.post("/api/v1/auth/register", json={
        "email": "me@example.com",
        "password": "Password123!"
    })
    login_res = await client.post("/api/v1/auth/login", json={
        "email": "me@example.com",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]

    me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "me@example.com"
