import pytest
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.schemas.product import ProductCreate
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_idempotency_key_prevents_duplicate_orders(client: AsyncClient, db_session: AsyncSession):
    # 1. Setup user & product
    user = await UserRepository.create(db_session, "idemp_user@test.com", "hash")
    product = await ProductRepository.create(db_session, ProductCreate(name="Limited Item", description="Desc", price=Decimal("100.00"), stock=5))
    
    # 2. Add product to cart
    cart = await CartRepository.get_or_create_by_user_id(db_session, user.id)
    await CartRepository.add_item(db_session, cart.id, product.id, 2)
    await db_session.commit()

    token = create_access_token(user.id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": "test_idempotency_key_001"
    }

    # 3. First checkout request
    res1 = await client.post("/api/v1/orders", headers=headers)
    assert res1.status_code == 201
    data1 = res1.json()
    order_id_1 = data1["id"]

    # Expire identity map cache to re-read updated database state
    product_id = product.id
    db_session.expire_all()
    refreshed_product = await ProductRepository.get_by_id(db_session, product_id)
    assert refreshed_product.stock == 3

    # 4. Duplicate checkout request with SAME Idempotency-Key
    res2 = await client.post("/api/v1/orders", headers=headers)
    assert res2.status_code == 201
    data2 = res2.json()
    order_id_2 = data2["id"]

    # Verify order IDs match (idempotent response)
    assert order_id_1 == order_id_2

    # Verify stock was NOT double-deducted (stock remains 3)
    db_session.expire_all()
    refreshed_product_2 = await ProductRepository.get_by_id(db_session, product_id)
    assert refreshed_product_2.stock == 3
