import json
import time
import uuid
from decimal import Decimal

from app.core.redis import get_arq_pool, get_redis
from app.models.order import Order
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.services.trace_service import TraceService
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


class OrderService:
    @staticmethod
    async def create_order_checkout(
        db: AsyncSession, user_id: uuid.UUID, idempotency_key: str | None = None
    ) -> Order:
        import hashlib

        start_time = time.time()

        # 1. Idempotency Check: if idempotency_key is provided, check if order already exists
        if idempotency_key:
            existing_order = await OrderRepository.get_by_idempotency_key(
                db, user_id, idempotency_key
            )
            if existing_order:
                cart_check = await CartRepository.get_by_user_id(db, user_id)
                if cart_check and cart_check.cart_items:
                    cart_repr_check = ",".join(
                        sorted(
                            [f"{item.product_id}:{item.quantity}" for item in cart_check.cart_items]
                        )
                    )
                    current_hash = hashlib.sha256(
                        f"{user_id}:{cart_repr_check}".encode()
                    ).hexdigest()
                    if existing_order.payload_hash and existing_order.payload_hash != current_hash:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Idempotency key reused with different request payload",
                        )
                return existing_order

        # 2. Fetch user's cart
        cart = await CartRepository.get_by_user_id(db, user_id)
        if not cart or not cart.cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot checkout with an empty cart"
            )

        # Compute payload hash (sorted item tuples: product_id:quantity)
        cart_repr = ",".join(
            sorted([f"{item.product_id}:{item.quantity}" for item in cart.cart_items])
        )
        payload_hash = hashlib.sha256(f"{user_id}:{cart_repr}".encode()).hexdigest()

        try:
            # 3. Eagerly lock products with FOR UPDATE in deterministic ID order to prevent deadlocks
            lock_start = time.time()
            product_ids = [item.product_id for item in cart.cart_items]
            locked_products = await ProductRepository.get_by_ids_for_update(db, product_ids)
            select_lock_ms = round((time.time() - lock_start) * 1000, 2)
            product_map = {p.id: p for p in locked_products}

            # 4. Check stock & calculate total
            total_amount = Decimal("0.00")
            order_items_to_create = []

            for item in cart.cart_items:
                product = product_map.get(item.product_id)
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Associated product '{item.product_id}' not found",
                    )

                if product.stock < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock}, requested: {item.quantity}",
                    )

                item_total = Decimal(str(product.price)) * Decimal(str(item.quantity))
                total_amount += item_total

                # Deduct stock on locked product instance
                product.stock -= item.quantity

                order_items_to_create.append(
                    {
                        "product_id": product.id,
                        "quantity": item.quantity,
                        "price": product.price,
                    }
                )

            # 5. Create Order & OrderItems
            order = await OrderRepository.create_order(
                db,
                user_id=user_id,
                status="CONFIRMED",
                total_amount=total_amount,
                idempotency_key=idempotency_key,
                payload_hash=payload_hash,
            )

            for item_data in order_items_to_create:
                await OrderRepository.add_order_item(
                    db,
                    order_id=order.id,
                    product_id=item_data["product_id"],
                    quantity=item_data["quantity"],
                    price=item_data["price"],
                )

            # 6. Clear Cart Items
            await CartRepository.clear_cart_items(db, cart)

            # 6b. Insert Transactional Outbox Event inside the SAME atomic SQL transaction
            from app.repositories.outbox_repository import OutboxRepository

            outbox_payload = json.dumps(
                {
                    "order_id": str(order.id),
                    "user_id": str(user_id),
                    "total_amount": str(total_amount),
                    "item_count": len(cart.cart_items),
                    "products": [
                        {"product_id": str(p.id), "name": p.name, "remaining_stock": p.stock}
                        for p in locked_products
                    ],
                }
            )
            await OutboxRepository.create_event(
                db, event_type="ORDER_CREATED", payload_json=outbox_payload
            )

            # 7. Commit transaction atomically
            commit_start = time.time()
            await db.commit()
            insert_order_ms = round((time.time() - commit_start) * 1000, 2)

            # 8. Invalidate product catalog cache upon stock update
            from app.services.cache_service import CacheService

            await CacheService.invalidate_product_cache()

            # 9. Post-Commit Asynchronous Task Offloading & Trace Recording
            arq_start = time.time()
            created_order = await OrderRepository.get_by_id_for_user(db, user_id, order.id)
            user_email = (
                created_order.user.email
                if (created_order and created_order.user)
                else "customer@example.com"
            )

            # Set initial order processing status in Redis
            redis = get_redis()
            if redis:
                await redis.setex(
                    f"order_status:{order.id}",
                    3600,
                    json.dumps(
                        {
                            "status": "Confirmed",
                            "updated_at": time.time(),
                            "detail": "Order saved to database; dispatching background worker tasks.",
                        }
                    ),
                )

            # Enqueue ARQ Tasks
            arq_pool = get_arq_pool()
            if arq_pool:
                try:
                    await arq_pool.enqueue_job(
                        "send_receipt_email",
                        str(order.id),
                        user_email,
                        str(total_amount),
                        _job_id=f"email_{order.id}",
                    )

                    product_audit_list = [
                        {"product_id": str(p.id), "name": p.name, "remaining_stock": p.stock}
                        for p in locked_products
                    ]
                    await arq_pool.enqueue_job(
                        "audit_low_stock", product_audit_list, _job_id=f"stock_{order.id}"
                    )

                    await arq_pool.enqueue_job(
                        "record_analytics_event",
                        "ORDER_PLACED",
                        {
                            "order_id": str(order.id),
                            "user_id": str(user_id),
                            "total_amount": str(total_amount),
                            "item_count": len(cart.cart_items),
                        },
                        _job_id=f"analytics_{order.id}",
                    )
                except Exception as e:
                    import logging

                    logging.getLogger(__name__).warning(f"Failed to enqueue ARQ tasks: {e}")

            arq_enqueue_ms = round((time.time() - arq_start) * 1000, 2)
            total_checkout_ms = round((time.time() - start_time) * 1000, 2)

            # Record OpenTelemetry-style Waterfall Trace
            trace_id = f"trace_{str(order.id)[:8]}"
            spans = [
                {
                    "service": "FastAPI",
                    "name": "POST /api/v1/orders/checkout",
                    "duration_ms": total_checkout_ms,
                },
                {
                    "service": "PostgreSQL",
                    "name": "SELECT FOR UPDATE (Locking)",
                    "duration_ms": select_lock_ms,
                },
                {
                    "service": "PostgreSQL",
                    "name": "INSERT order & order_items",
                    "duration_ms": insert_order_ms,
                },
                {
                    "service": "Redis ARQ",
                    "name": "Enqueue Worker Tasks",
                    "duration_ms": arq_enqueue_ms,
                },
            ]
            await TraceService.record_trace(
                trace_id, "POST /api/v1/orders/checkout", total_checkout_ms, spans
            )

            return created_order or order

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Checkout failed: {str(e)}",
            )

    @staticmethod
    async def get_user_orders(db: AsyncSession, user_id: uuid.UUID) -> list[Order]:
        return await OrderRepository.list_by_user_id(db, user_id)

    @staticmethod
    async def get_user_order_by_id(
        db: AsyncSession, user_id: uuid.UUID, order_id: uuid.UUID
    ) -> Order:
        order = await OrderRepository.get_by_id_for_user(db, user_id, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return order
