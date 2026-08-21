import logging
from arq.connections import RedisSettings
from app.core.config import settings
from app.tasks.order_tasks import send_receipt_email, audit_low_stock, record_analytics_event
from app.tasks.outbox_processor import process_outbox_events

logger = logging.getLogger(__name__)

async def startup(ctx: dict) -> None:
    logger.info("ARQ Background Worker started up successfully.")

async def shutdown(ctx: dict) -> None:
    logger.info("ARQ Background Worker shutting down.")

class WorkerSettings:
    functions = [send_receipt_email, audit_low_stock, record_analytics_event, process_outbox_events]

    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
    max_tries = settings.TASK_MAX_RETRIES
