import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


async def send_receipt_email(
    ctx: dict[str, Any], order_id: str, user_email: str, total_amount: str
) -> dict[str, Any]:
    start_time = time.time()
    logger.info(f"[ARQ Task] Starting send_receipt_email for order={order_id}, user={user_email}")

    # Simulate processing time for sending email
    time.sleep(0.05) if "redis" not in ctx else None

    redis = ctx.get("redis")
    if redis:
        # Update order status state in Redis
        await redis.setex(
            f"order_status:{order_id}",
            3600,
            json.dumps(
                {
                    "status": "Receipt Emailed",
                    "updated_at": time.time(),
                    "detail": f"Simulated receipt email sent to {user_email} (Total: ${total_amount})",
                }
            ),
        )

        # Append notification to user inbox
        notification = {
            "id": f"notif_{order_id[:8]}",
            "type": "RECEIPT",
            "title": "Order Receipt Confirmed",
            "message": f"Your order #{order_id[:8]} for ${total_amount} has been processed successfully.",
            "timestamp": time.time(),
        }
        await redis.lpush(f"user_notifications:{user_email}", json.dumps(notification))
        await redis.ltrim(f"user_notifications:{user_email}", 0, 19)

        # Log worker execution job for admin observability
        duration_ms = round((time.time() - start_time) * 1000, 2)
        job_log = {
            "job_name": "send_receipt_email",
            "order_id": order_id,
            "status": "SUCCESS",
            "duration_ms": duration_ms,
            "timestamp": time.time(),
        }
        await redis.lpush("arq_job_logs", json.dumps(job_log))
        await redis.ltrim("arq_job_logs", 0, 49)

    logger.info(f"[ARQ Task] Completed send_receipt_email for order={order_id}")
    return {"status": "success", "order_id": order_id, "user_email": user_email}


async def audit_low_stock(
    ctx: dict[str, Any], product_items: list[dict[str, Any]]
) -> dict[str, Any]:
    logger.info(f"[ARQ Task] Executing audit_low_stock for {len(product_items)} items")
    redis = ctx.get("redis")
    low_stock_flagged = []

    for item in product_items:
        prod_id = item.get("product_id")
        prod_name = item.get("name", "Product")
        remaining_stock = item.get("remaining_stock", 0)

        if remaining_stock <= 5:
            low_stock_flagged.append({"id": prod_id, "name": prod_name, "stock": remaining_stock})
            if redis:
                await redis.setex(
                    f"low_stock_alert:{prod_id}",
                    86400,
                    json.dumps(
                        {
                            "product_id": prod_id,
                            "product_name": prod_name,
                            "stock": remaining_stock,
                            "timestamp": time.time(),
                        }
                    ),
                )

                # Push low stock notification to admin / general inbox
                alert_notif = {
                    "id": f"alert_{prod_id[:8]}",
                    "type": "STOCK_ALERT",
                    "title": "Low Stock Warning",
                    "message": f"'{prod_name}' has only {remaining_stock} units left in stock!",
                    "timestamp": time.time(),
                }
                await redis.lpush("global_notifications", json.dumps(alert_notif))
                await redis.ltrim("global_notifications", 0, 19)

    logger.info(f"[ARQ Task] Completed audit_low_stock. Flagged {len(low_stock_flagged)} items")
    return {"status": "success", "low_stock_items": low_stock_flagged}


async def record_analytics_event(
    ctx: dict[str, Any], event_type: str, payload: dict[str, Any]
) -> dict[str, Any]:
    redis = ctx.get("redis")
    if redis:
        try:
            if event_type == "ORDER_PLACED":
                amount = float(payload.get("total_amount", 0.0))
                await redis.incrbyfloat("analytics:total_revenue", amount)
                await redis.incr("analytics:total_orders")

            event_log = {"event_type": event_type, "payload": payload, "timestamp": time.time()}
            await redis.lpush("analytics_events", json.dumps(event_log))
            await redis.ltrim("analytics_events", 0, 99)
        except Exception as e:
            logger.warning(f"Failed to record analytics event: {e}")

    return {"status": "success", "event_type": event_type}
