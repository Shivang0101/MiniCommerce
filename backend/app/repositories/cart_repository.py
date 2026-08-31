import uuid

from app.models.cart import Cart, CartItem
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class CartRepository:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> Cart | None:
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.cart_items).selectinload(CartItem.product))
            .execution_options(populate_existing=True)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_or_create_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> Cart:
        cart = await CartRepository.get_by_user_id(db, user_id)
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            await db.commit()
            await db.refresh(cart)
            cart = await CartRepository.get_by_user_id(db, user_id)
        return cart

    @staticmethod
    async def get_item_by_id(db: AsyncSession, item_id: uuid.UUID) -> CartItem | None:
        stmt = (
            select(CartItem).where(CartItem.id == item_id).options(selectinload(CartItem.product))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_item_by_cart_and_product(
        db: AsyncSession, cart_id: uuid.UUID, product_id: uuid.UUID
    ) -> CartItem | None:
        stmt = (
            select(CartItem)
            .where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            .options(selectinload(CartItem.product))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def add_item(
        db: AsyncSession, cart_id: uuid.UUID, product_id: uuid.UUID, quantity: int
    ) -> CartItem:
        item = await CartRepository.get_item_by_cart_and_product(db, cart_id, product_id)
        if item:
            item.quantity += quantity
        else:
            item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
            db.add(item)
        await db.commit()
        return await CartRepository.get_item_by_id(db, item.id)

    @staticmethod
    async def update_item_quantity(
        db: AsyncSession, item_id: uuid.UUID, quantity: int
    ) -> CartItem | None:
        item = await CartRepository.get_item_by_id(db, item_id)
        if not item:
            return None
        item.quantity = quantity
        await db.commit()
        return item

    @staticmethod
    async def delete_item(db: AsyncSession, item_id: uuid.UUID) -> bool:
        item = await CartRepository.get_item_by_id(db, item_id)
        if not item:
            return False
        await db.delete(item)
        await db.commit()
        return True

    @staticmethod
    async def clear_cart_items(db: AsyncSession, cart: Cart) -> None:
        for item in list(cart.cart_items):
            await db.delete(item)
