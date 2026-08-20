import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.product import ProductCreate

@pytest.mark.asyncio
async def test_user_repository(db_session: AsyncSession):
    user = await UserRepository.create(db_session, "repo_user@test.com", "hashed_secret")
    assert user.id is not None
    assert user.email == "repo_user@test.com"

    fetched = await UserRepository.get_by_email(db_session, "repo_user@test.com")
    assert fetched is not None
    assert fetched.id == user.id

@pytest.mark.asyncio
async def test_product_repository_pagination_and_sorting(db_session: AsyncSession):
    await ProductRepository.create(db_session, ProductCreate(name="Alpha Phone", description="Desc A", price=Decimal("500.00"), stock=10))
    await ProductRepository.create(db_session, ProductCreate(name="Beta Laptop", description="Desc B", price=Decimal("1200.00"), stock=5))
    await ProductRepository.create(db_session, ProductCreate(name="Gamma Monitor", description="Desc C", price=Decimal("300.00"), stock=15))

    # Test sorting by price asc
    products, total = await ProductRepository.list_products(db_session, page=1, page_size=2, sort_by="price", sort_order="asc")
    assert total == 3
    assert len(products) == 2
    assert products[0].name == "Gamma Monitor"
    assert products[1].name == "Alpha Phone"

    # Test price filtering
    filtered, f_total = await ProductRepository.list_products(db_session, min_price=Decimal("400.00"), max_price=Decimal("1000.00"))
    assert f_total == 1
    assert filtered[0].name == "Alpha Phone"

@pytest.mark.asyncio
async def test_order_repository_idempotency(db_session: AsyncSession):
    user = await UserRepository.create(db_session, "idemp_repo@test.com", "hash")
    order1 = await OrderRepository.create_order(
        db_session, user_id=user.id, status="CONFIRMED", total_amount=Decimal("99.99"), idempotency_key="unique_key_123"
    )
    await db_session.commit()

    fetched = await OrderRepository.get_by_idempotency_key(db_session, user.id, "unique_key_123")
    assert fetched is not None
    assert fetched.id == order1.id
