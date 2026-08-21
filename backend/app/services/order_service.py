import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository

class OrderService:
    @staticmethod
    async def create_order_checkout(
        db: AsyncSession, 
        user_id: uuid.UUID, 
        idempotency_key: str | None = None
    ) -> Order:
        # 1. Idempotency Check: if idempotency_key is provided, check if order already exists
        if idempotency_key:
            existing_order = await OrderRepository.get_by_idempotency_key(db, user_id, idempotency_key)
            if existing_order:
                return existing_order

        try:
            # 2. Fetch user's cart
            cart = await CartRepository.get_by_user_id(db, user_id)
            if not cart or not cart.cart_items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot checkout with an empty cart"
                )

            # 3. Eagerly lock products with FOR UPDATE in deterministic ID order to prevent deadlocks
            product_ids = [item.product_id for item in cart.cart_items]
            locked_products = await ProductRepository.get_by_ids_for_update(db, product_ids)
            product_map = {p.id: p for p in locked_products}

            # 4. Check stock & calculate total
            total_amount = Decimal("0.00")
            order_items_to_create = []

            for item in cart.cart_items:
                product = product_map.get(item.product_id)
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Associated product '{item.product_id}' not found"
                    )

                if product.stock < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock}, requested: {item.quantity}"
                    )

                item_total = Decimal(str(product.price)) * Decimal(str(item.quantity))
                total_amount += item_total

                # Deduct stock on locked product instance
                product.stock -= item.quantity

                order_items_to_create.append({
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "price": product.price,
                })

            # 5. Create Order & OrderItems
            order = await OrderRepository.create_order(
                db,
                user_id=user_id,
                status="CONFIRMED",
                total_amount=total_amount,
                idempotency_key=idempotency_key
            )

            for item_data in order_items_to_create:
                await OrderRepository.add_order_item(
                    db,
                    order_id=order.id,
                    product_id=item_data["product_id"],
                    quantity=item_data["quantity"],
                    price=item_data["price"]
                )

            # 6. Clear Cart Items
            await CartRepository.clear_cart_items(db, cart)

            # 7. Commit transaction atomically
            await db.commit()

            # 8. Invalidate product catalog cache upon stock update
            from app.services.cache_service import CacheService
            await CacheService.invalidate_product_cache()

            # Return eagerly loaded created order
            return await OrderRepository.get_by_id_for_user(db, user_id, order.id)

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
        return await OrderRepository.list_by_user_id(db, user_id)

    @staticmethod
    async def get_user_order_by_id(db: AsyncSession, user_id: uuid.UUID, order_id: uuid.UUID) -> Order:
        order = await OrderRepository.get_by_id_for_user(db, user_id, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return order
