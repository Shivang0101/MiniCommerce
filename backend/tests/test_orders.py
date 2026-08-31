import pytest
from httpx import AsyncClient


async def get_auth_headers(client: AsyncClient, email: str) -> dict:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!"})
    login_res = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "Password123!"}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_empty_cart_checkout(client: AsyncClient):
    headers = await get_auth_headers(client, "emptycart@example.com")
    res = await client.post("/api/v1/orders", headers=headers)
    assert res.status_code == 400
    assert "empty cart" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_successful_checkout(client: AsyncClient):
    headers = await get_auth_headers(client, "buyer@example.com")

    # Create product with stock 10
    prod_res = await client.post(
        "/api/v1/products", json={"name": "Monitor", "price": 300.0, "stock": 10}
    )
    prod_id = prod_res.json()["id"]

    # Add 3 items to cart
    await client.post(
        "/api/v1/cart/items", headers=headers, json={"product_id": prod_id, "quantity": 3}
    )

    # Checkout
    order_res = await client.post("/api/v1/orders", headers=headers)
    assert order_res.status_code == 201
    order_data = order_res.json()
    assert order_data["status"] == "CONFIRMED"
    assert float(order_data["total_amount"]) == 900.0
    assert len(order_data["order_items"]) == 1
    assert order_data["order_items"][0]["quantity"] == 3
    assert float(order_data["order_items"][0]["price"]) == 300.0

    # Verify cart is now empty
    cart_res = await client.get("/api/v1/cart", headers=headers)
    assert len(cart_res.json()["cart_items"]) == 0

    # Verify product stock was reduced from 10 to 7
    prod_check = await client.get(f"/api/v1/products/{prod_id}")
    assert prod_check.json()["stock"] == 7


@pytest.mark.asyncio
async def test_order_ownership(client: AsyncClient):
    h1 = await get_auth_headers(client, "owner1@example.com")
    h2 = await get_auth_headers(client, "owner2@example.com")

    prod = await client.post("/api/v1/products", json={"name": "Item", "price": 10.0, "stock": 10})
    prod_id = prod.json()["id"]

    await client.post("/api/v1/cart/items", headers=h1, json={"product_id": prod_id, "quantity": 1})
    order_res = await client.post("/api/v1/orders", headers=h1)
    order_id = order_res.json()["id"]

    # Owner 1 can access
    o1_res = await client.get(f"/api/v1/orders/{order_id}", headers=h1)
    assert o1_res.status_code == 200

    # Owner 2 denied
    o2_res = await client.get(f"/api/v1/orders/{order_id}", headers=h2)
    assert o2_res.status_code == 404
