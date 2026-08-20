import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderItem

class OrderRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, order_id: uuid.UUID) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.order_items).selectinload(OrderItem.product))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id_for_user(db: AsyncSession, user_id: uuid.UUID, order_id: uuid.UUID) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
            .options(selectinload(Order.order_items).selectinload(OrderItem.product))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_idempotency_key(db: AsyncSession, user_id: uuid.UUID, idempotency_key: str) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id, Order.idempotency_key == idempotency_key)
            .options(selectinload(Order.order_items).selectinload(OrderItem.product))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.order_items).selectinload(OrderItem.product))
            .order_by(Order.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_order(
        db: AsyncSession,
        user_id: uuid.UUID,
        status: str,
        total_amount: Decimal,
        idempotency_key: str | None = None
    ) -> Order:
        order = Order(
            user_id=user_id,
            status=status,
            total_amount=total_amount,
            idempotency_key=idempotency_key
        )
        db.add(order)
        await db.flush()
        return order

    @staticmethod
    async def add_order_item(
        db: AsyncSession,
        order_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: int,
        price: Decimal
    ) -> OrderItem:
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price
        )
        db.add(item)
        return item
