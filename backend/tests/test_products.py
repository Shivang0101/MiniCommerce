import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient):
    payload = {
        "name": "Test Product",
        "description": "Awesome product description",
        "price": 99.99,
        "stock": 10,
    }
    response = await client.post("/api/v1/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert float(data["price"]) == 99.99
    assert data["stock"] == 10
    assert "id" in data


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient):
    await client.post("/api/v1/products", json={"name": "Prod A", "price": 10.0, "stock": 5})
    await client.post("/api/v1/products", json={"name": "Prod B", "price": 20.0, "stock": 15})

    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 2


@pytest.mark.asyncio
async def test_get_product(client: AsyncClient):
    create_res = await client.post(
        "/api/v1/products", json={"name": "Single Prod", "price": 50.0, "stock": 20}
    )
    prod_id = create_res.json()["id"]

    get_res = await client.get(f"/api/v1/products/{prod_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Single Prod"


@pytest.mark.asyncio
async def test_get_missing_product(client: AsyncClient):
    random_uuid = str(uuid.uuid4())
    res = await client.get(f"/api/v1/products/{random_uuid}")
    assert res.status_code == 404
    assert res.json()["detail"] == "Product not found"
