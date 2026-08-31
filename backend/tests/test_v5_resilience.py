import pytest
from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    breaker = CircuitBreaker(
        "test_cb", failure_threshold=0.5, recovery_time_seconds=0.2, min_requests=2
    )
    assert breaker.state == "CLOSED"

    async def fail_func():
        raise ValueError("Simulated downstream error")

    # Trigger failures
    for _ in range(2):
        with pytest.raises(ValueError):
            await breaker.call(fail_func)

    assert breaker.state == "OPEN"

    # Call while OPEN raises CircuitBreakerOpenException
    with pytest.raises(CircuitBreakerOpenException):
        await breaker.call(fail_func)


@pytest.mark.asyncio
async def test_payload_hashed_idempotency_conflict(client: AsyncClient):
    # Register & Login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "hash_idem@example.com",
            "password": "Password123!",
            "role": "STORE_MANAGER",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login", json={"email": "hash_idem@example.com", "password": "Password123!"}
    )

    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create product & add to cart
    prod_res = await client.post(
        "/api/v1/products",
        json={"name": "Idem Mouse", "price": 49.99, "stock": 10},
        headers=headers,
    )
    prod_id = prod_res.json()["id"]
    await client.post(
        "/api/v1/cart/items", json={"product_id": prod_id, "quantity": 1}, headers=headers
    )

    # First checkout with Idempotency Key
    idemp_key = "idemp_test_hash_123"
    checkout_1 = await client.post(
        "/api/v1/orders", headers={"Authorization": f"Bearer {token}", "Idempotency-Key": idemp_key}
    )
    assert checkout_1.status_code == 201

    # Retry same checkout with SAME key -> Returns original order
    checkout_2 = await client.post(
        "/api/v1/orders", headers={"Authorization": f"Bearer {token}", "Idempotency-Key": idemp_key}
    )
    assert checkout_2.status_code == 201
    assert checkout_2.json()["id"] == checkout_1.json()["id"]

    # Add a different item to cart and reuse same key -> 409 Conflict
    prod2_res = await client.post(
        "/api/v1/products",
        json={"name": "Idem Keyboard", "price": 99.99, "stock": 10},
        headers=headers,
    )
    prod2_id = prod2_res.json()["id"]
    await client.post(
        "/api/v1/cart/items", json={"product_id": prod2_id, "quantity": 2}, headers=headers
    )

    conflict_res = await client.post(
        "/api/v1/orders", headers={"Authorization": f"Bearer {token}", "Idempotency-Key": idemp_key}
    )
    assert conflict_res.status_code == 409
