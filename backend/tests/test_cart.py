import pytest
from httpx import AsyncClient


async def get_authenticated_headers(client: AsyncClient, email: str) -> dict:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!"})
    login_res = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "Password123!"}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_add_item_and_get_cart(client: AsyncClient):
    headers = await get_authenticated_headers(client, "cart1@example.com")

    prod_res = await client.post(
        "/api/v1/products", json={"name": "Mouse", "price": 25.0, "stock": 10}
    )
    prod_id = prod_res.json()["id"]

    add_res = await client.post(
        "/api/v1/cart/items", headers=headers, json={"product_id": prod_id, "quantity": 2}
    )
    assert add_res.status_code == 200
    cart_data = add_res.json()
    assert len(cart_data["cart_items"]) == 1
    assert cart_data["cart_items"][0]["quantity"] == 2
    assert cart_data["cart_items"][0]["product"]["id"] == prod_id


@pytest.mark.asyncio
async def test_update_item_quantity(client: AsyncClient):
    headers = await get_authenticated_headers(client, "cart2@example.com")
    prod_res = await client.post(
        "/api/v1/products", json={"name": "Keyboard", "price": 100.0, "stock": 5}
    )
    prod_id = prod_res.json()["id"]

    add_res = await client.post(
        "/api/v1/cart/items", headers=headers, json={"product_id": prod_id, "quantity": 1}
    )
    item_id = add_res.json()["cart_items"][0]["id"]

    update_res = await client.patch(
        f"/api/v1/cart/items/{item_id}", headers=headers, json={"quantity": 3}
    )
    assert update_res.status_code == 200
    assert update_res.json()["cart_items"][0]["quantity"] == 3


@pytest.mark.asyncio
async def test_remove_cart_item(client: AsyncClient):
    headers = await get_authenticated_headers(client, "cart3@example.com")
    prod_res = await client.post(
        "/api/v1/products", json={"name": "Pad", "price": 15.0, "stock": 5}
    )
    prod_id = prod_res.json()["id"]

    add_res = await client.post(
        "/api/v1/cart/items", headers=headers, json={"product_id": prod_id, "quantity": 1}
    )
    item_id = add_res.json()["cart_items"][0]["id"]

    del_res = await client.delete(f"/api/v1/cart/items/{item_id}", headers=headers)
    assert del_res.status_code == 200
    assert len(del_res.json()["cart_items"]) == 0


@pytest.mark.asyncio
async def test_stock_validation(client: AsyncClient):
    headers = await get_authenticated_headers(client, "cart4@example.com")
    prod_res = await client.post(
        "/api/v1/products", json={"name": "Rare Item", "price": 500.0, "stock": 2}
    )
    prod_id = prod_res.json()["id"]

    # Try adding more than available stock
    fail_res = await client.post(
        "/api/v1/cart/items", headers=headers, json={"product_id": prod_id, "quantity": 5}
    )
    assert fail_res.status_code == 400
    assert "exceeds available stock" in fail_res.json()["detail"]


@pytest.mark.asyncio
async def test_cart_ownership_validation(client: AsyncClient):
    headers_user1 = await get_authenticated_headers(client, "user1@example.com")
    headers_user2 = await get_authenticated_headers(client, "user2@example.com")

    prod_res = await client.post(
        "/api/v1/products", json={"name": "Shared Prod", "price": 10.0, "stock": 10}
    )
    prod_id = prod_res.json()["id"]

    # User 1 adds item
    u1_cart = await client.post(
        "/api/v1/cart/items", headers=headers_user1, json={"product_id": prod_id, "quantity": 1}
    )
    item_id = u1_cart.json()["cart_items"][0]["id"]

    # User 2 attempts to modify User 1's cart item
    u2_hack = await client.patch(
        f"/api/v1/cart/items/{item_id}", headers=headers_user2, json={"quantity": 2}
    )
    assert u2_hack.status_code == 404
    assert u2_hack.json()["detail"] == "Cart item not found"
