import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_keyset_pagination_and_soft_delete(client: AsyncClient):
    # Register store manager
    await client.post(
        "/api/v1/auth/register",
        json={"email": "data_mgr@example.com", "password": "Password123!", "role": "STORE_MANAGER"},
    )
    login_res = await client.post(
        "/api/v1/auth/login", json={"email": "data_mgr@example.com", "password": "Password123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create 3 products
    p1 = (
        await client.post(
            "/api/v1/products", json={"name": "Item A", "price": 10.0, "stock": 5}, headers=headers
        )
    ).json()
    p2 = (
        await client.post(
            "/api/v1/products", json={"name": "Item B", "price": 20.0, "stock": 5}, headers=headers
        )
    ).json()
    p3 = (
        await client.post(
            "/api/v1/products", json={"name": "Item C", "price": 30.0, "stock": 5}, headers=headers
        )
    ).json()

    # Test Keyset Pagination
    keyset_res = await client.get("/api/v1/products/keyset?limit=2")
    assert keyset_res.status_code == 200
    keyset_items = keyset_res.json()
    assert len(keyset_items) <= 2

    # Soft Delete Item B
    del_res = await client.delete(f"/api/v1/products/{p2['id']}", headers=headers)
    assert del_res.status_code == 204

    # GET missing item B -> 404 Not Found
    get_del = await client.get(f"/api/v1/products/{p2['id']}")
    assert get_del.status_code == 404

    # List catalog should not include Item B
    list_res = await client.get("/api/v1/products")
    product_ids = [p["id"] for p in list_res.json()]
    assert p2["id"] not in product_ids
