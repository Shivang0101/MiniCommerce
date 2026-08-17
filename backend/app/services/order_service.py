import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.order import Order, OrderItem

class OrderService:
    @staticmethod
    async def create_order_checkout(db: AsyncSession, user_id: uuid.UUID) -> Order:
        try:
            # 1. Fetch user's cart with cart items and products eagerly loaded
            cart_stmt = (
                select(Cart)
                .where(Cart.user_id == user_id)
                .options(selectinload(Cart.cart_items).selectinload(CartItem.product))
                .execution_options(populate_existing=True)
            )
            cart_res = await db.execute(cart_stmt)
            cart = cart_res.scalar_one_or_none()

            if not cart or not cart.cart_items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot checkout with an empty cart"
                )

            # 2. Check stock & calculate total
            total_amount = Decimal("0.00")
            order_items_to_create = []

            for item in cart.cart_items:
                product = item.product
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Associated product not found"
                    )

                if product.stock < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock}, requested: {item.quantity}"
                    )

                item_total = Decimal(str(product.price)) * Decimal(str(item.quantity))
                total_amount += item_total

                # Deduct stock
                product.stock -= item.quantity

                order_items_to_create.append({
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "price": product.price, # Snapshot current price
                })

            # 3. Create Order
            order = Order(
                user_id=user_id,
                status="CONFIRMED",
                total_amount=total_amount
            )
            db.add(order)
            await db.flush() # Populate order.id

            # 4. Create OrderItems
            for item_data in order_items_to_create:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data["product_id"],
                    quantity=item_data["quantity"],
                    price=item_data["price"]
                )
                db.add(order_item)

            # 5. Delete Cart Items
            for item in list(cart.cart_items):
                await db.delete(item)

            # Commit the transaction atomically
            await db.commit()

            # Return order eagerly loaded
            return await OrderService.get_user_order_by_id(db, user_id, order.id)

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Checkout failed: {str(e)}"
            )

    @staticmethod
    async def get_user_orders(db: AsyncSession, user_id: uuid.UUID) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.product)
            )
            .execution_options(populate_existing=True)
            .order_by(Order.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_order_by_id(db: AsyncSession, user_id: uuid.UUID, order_id: uuid.UUID) -> Order:
        stmt = (
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.product)
            )
            .execution_options(populate_existing=True)
        )
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return order
