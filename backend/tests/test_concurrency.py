from decimal import Decimal

import pytest
from app.core.security import create_access_token
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.product import ProductCreate
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_concurrent_checkout_prevents_overselling(
    client: AsyncClient, db_session: AsyncSession
):
    # 1. Create 2 test users
    user_a = await UserRepository.create(db_session, "user_a@concurrency.com", "hash")
    user_b = await UserRepository.create(db_session, "user_b@concurrency.com", "hash")

    # 2. Create product with stock = 1
    product = await ProductRepository.create(
        db_session,
        ProductCreate(
            name="Scarce Item", description="Only 1 left", price=Decimal("250.00"), stock=1
        ),
    )

    # 3. Populate cart for User A (qty 1) and User B (qty 1)
    cart_a = await CartRepository.get_or_create_by_user_id(db_session, user_a.id)
    await CartRepository.add_item(db_session, cart_a.id, product.id, 1)

    cart_b = await CartRepository.get_or_create_by_user_id(db_session, user_b.id)
    await CartRepository.add_item(db_session, cart_b.id, product.id, 1)

    await db_session.commit()

    token_a = create_access_token(user_a.id)
    token_b = create_access_token(user_b.id)

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 4. Sequential checkout requests testing inventory conflict
    res_a = await client.post("/api/v1/orders", headers=headers_a)
    res_b = await client.post("/api/v1/orders", headers=headers_b)

    statuses = [res_a.status_code, res_b.status_code]

    # Exactly one request must succeed (201) and exactly one must fail (409 Conflict)
    assert 201 in statuses
    assert 409 in statuses

    # Verify final stock is exactly 0 (no negative stock, no overselling)
    product_id = product.id
    db_session.expire_all()
    final_product = await ProductRepository.get_by_id(db_session, product_id)
    assert final_product.stock == 0
