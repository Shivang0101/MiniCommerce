import pytest
from app.core.security import create_access_token, create_refresh_token, decode_access_token
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dual_token_generation():
    access_tok = create_access_token(subject="user_123", scopes=["products:read"])
    refresh_tok = create_refresh_token(subject="user_123")

    acc_payload = decode_access_token(access_tok)
    ref_payload = decode_access_token(refresh_tok)

    assert acc_payload["type"] == "access"
    assert acc_payload["jti"] is not None
    assert "products:read" in acc_payload["scopes"]

    assert ref_payload["type"] == "refresh"
    assert ref_payload["jti"] is not None


@pytest.mark.asyncio
async def test_register_and_login_with_refresh_cookie(client: AsyncClient):
    res_reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "v5sec@example.com", "password": "Password123!", "role": "STORE_MANAGER"},
    )
    assert res_reg.status_code == 201
    assert res_reg.json()["role"] == "STORE_MANAGER"

    res_login = await client.post(
        "/api/v1/auth/login", json={"email": "v5sec@example.com", "password": "Password123!"}
    )
    assert res_login.status_code == 200
    login_data = res_login.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data


@pytest.mark.asyncio
async def test_rbac_scope_protection(client: AsyncClient):
    # Register customer
    await client.post(
        "/api/v1/auth/register",
        json={"email": "cust_rbac@example.com", "password": "Password123!", "role": "CUSTOMER"},
    )
    res_cust_login = await client.post(
        "/api/v1/auth/login", json={"email": "cust_rbac@example.com", "password": "Password123!"}
    )
    cust_token = res_cust_login.json()["access_token"]

    # Customer trying to create product (requires products:write) -> 403 Forbidden
    res_create = await client.post(
        "/api/v1/products",
        json={"name": "Forbidden Keyboard", "price": 99.99, "stock": 10},
        headers={"Authorization": f"Bearer {cust_token}"},
    )
    assert res_create.status_code == 403

    # Register Store Manager
    await client.post(
        "/api/v1/auth/register",
        json={"email": "mgr_rbac@example.com", "password": "Password123!", "role": "STORE_MANAGER"},
    )
    res_mgr_login = await client.post(
        "/api/v1/auth/login", json={"email": "mgr_rbac@example.com", "password": "Password123!"}
    )
    mgr_token = res_mgr_login.json()["access_token"]

    # Store Manager creating product -> 201 Created
    res_mgr_create = await client.post(
        "/api/v1/products",
        json={"name": "Allowed Keyboard", "price": 149.99, "stock": 25},
        headers={"Authorization": f"Bearer {mgr_token}"},
    )
    assert res_mgr_create.status_code == 201
