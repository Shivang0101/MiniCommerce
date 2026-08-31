import json
import logging

from app.core.redis import get_arq_pool
from app.db.session import AsyncSessionLocal
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


async def process_outbox_events(ctx: dict) -> dict:
    """Polls PENDING outbox records, enqueues corresponding ARQ jobs, and marks records as PROCESSED."""
    processed_count = 0
    async with AsyncSessionLocal() as db:
        pending_events = await OutboxRepository.get_pending_events(db, limit=20)
        if not pending_events:
            return {"status": "SUCCESS", "processed_events": 0}

        arq_pool = get_arq_pool()
        for event in pending_events:
            try:
                payload = json.loads(event.payload_json)
                if event.event_type == "ORDER_CREATED" and arq_pool:
                    order_id = payload.get("order_id")
                    user_id = payload.get("user_id")
                    total_amount = payload.get("total_amount")
                    products = payload.get("products", [])

                    user_email = "customer@example.com"
                    if user_id:
                        import uuid

                        user = await UserRepository.get_by_id(db, uuid.UUID(user_id))
                        if user:
                            user_email = user.email

                    # Enqueue tasks to ARQ
                    await arq_pool.enqueue_job(
                        "send_receipt_email",
                        order_id,
                        user_email,
                        total_amount,
                        _job_id=f"outbox_email_{order_id}",
                    )
                    await arq_pool.enqueue_job(
                        "audit_low_stock", products, _job_id=f"outbox_stock_{order_id}"
                    )
                    await arq_pool.enqueue_job(
                        "record_analytics_event",
                        "OUTBOX_ORDER_PLACED",
                        payload,
                        _job_id=f"outbox_analytics_{order_id}",
                    )

                await OutboxRepository.mark_event_processed(db, event.id)
                processed_count += 1
            except Exception as e:
                logger.error(f"Error processing outbox event {event.id}: {e}")
                failed_event = await OutboxRepository.mark_event_failed(
                    db, event.id, str(e), max_retries=event.max_retries
                )
                if failed_event and failed_event.status == "DEAD_LETTER":
                    logger.warning(
                        f"Outbox event {event.id} transitioned to DEAD_LETTER status after {failed_event.retry_count} failed retries."
                    )

    logger.info(f"Outbox Processor completed. Processed {processed_count} events.")
    return {"status": "SUCCESS", "processed_events": processed_count}
