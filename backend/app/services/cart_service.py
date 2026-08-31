import uuid

from app.models.cart import Cart
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartItemCreate, CartItemUpdate
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


class CartService:
    @staticmethod
    async def get_or_create_cart(db: AsyncSession, user_id: uuid.UUID) -> Cart:
        return await CartRepository.get_or_create_by_user_id(db, user_id)

    @staticmethod
    async def add_item(db: AsyncSession, user_id: uuid.UUID, item_in: CartItemCreate) -> Cart:
        cart = await CartService.get_or_create_cart(db, user_id)

        product = await ProductRepository.get_by_id(db, item_in.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        existing_item = next(
            (item for item in cart.cart_items if item.product_id == item_in.product_id), None
        )
        current_qty = existing_item.quantity if existing_item else 0
        new_qty = current_qty + item_in.quantity

        if new_qty > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({new_qty}) exceeds available stock ({product.stock})",
            )

        await CartRepository.add_item(db, cart.id, item_in.product_id, item_in.quantity)
        return await CartService.get_or_create_cart(db, user_id)

    @staticmethod
    async def update_item_quantity(
        db: AsyncSession, user_id: uuid.UUID, cart_item_id: uuid.UUID, item_in: CartItemUpdate
    ) -> Cart:
        cart = await CartService.get_or_create_cart(db, user_id)

        cart_item = next((item for item in cart.cart_items if item.id == cart_item_id), None)
        if not cart_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

        product = cart_item.product
        if item_in.quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({item_in.quantity}) exceeds available stock ({product.stock})",
            )

        await CartRepository.update_item_quantity(db, cart_item_id, item_in.quantity)
        return await CartService.get_or_create_cart(db, user_id)

    @staticmethod
    async def remove_item(db: AsyncSession, user_id: uuid.UUID, cart_item_id: uuid.UUID) -> Cart:
        cart = await CartService.get_or_create_cart(db, user_id)

        cart_item = next((item for item in cart.cart_items if item.id == cart_item_id), None)
        if not cart_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

        await CartRepository.delete_item(db, cart_item_id)
        return await CartService.get_or_create_cart(db, user_id)
