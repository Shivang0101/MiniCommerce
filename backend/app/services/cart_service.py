import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartItemUpdate

class CartService:
    @staticmethod
    async def get_or_create_cart(db: AsyncSession, user_id: uuid.UUID) -> Cart:
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.cart_items).selectinload(CartItem.product))
            .execution_options(populate_existing=True)
        )
        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            await db.commit()
            result = await db.execute(stmt)
            cart = result.scalar_one()

        return cart

    @staticmethod
    async def add_item(db: AsyncSession, user_id: uuid.UUID, item_in: CartItemCreate) -> Cart:
        cart = await CartService.get_or_create_cart(db, user_id)
        
        # Check product existence
        product_stmt = select(Product).where(Product.id == item_in.product_id)
        product_res = await db.execute(product_stmt)
        product = product_res.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Find if item already exists in cart
        existing_item = next((item for item in cart.cart_items if item.product_id == item_in.product_id), None)
        current_qty = existing_item.quantity if existing_item else 0
        new_qty = current_qty + item_in.quantity

        if new_qty > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({new_qty}) exceeds available stock ({product.stock})"
            )

        if existing_item:
            existing_item.quantity = new_qty
        else:
            new_item = CartItem(
                cart_id=cart.id,
                product_id=item_in.product_id,
                quantity=item_in.quantity
            )
            db.add(new_item)

        await db.commit()
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
                detail=f"Requested quantity ({item_in.quantity}) exceeds available stock ({product.stock})"
            )

        cart_item.quantity = item_in.quantity
        await db.commit()
        return await CartService.get_or_create_cart(db, user_id)

    @staticmethod
    async def remove_item(db: AsyncSession, user_id: uuid.UUID, cart_item_id: uuid.UUID) -> Cart:
        cart = await CartService.get_or_create_cart(db, user_id)
        
        cart_item = next((item for item in cart.cart_items if item.id == cart_item_id), None)
        if not cart_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

        await db.delete(cart_item)
        await db.commit()
        return await CartService.get_or_create_cart(db, user_id)
