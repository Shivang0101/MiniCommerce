import logging

from app.core.config import settings
from app.tasks.order_tasks import audit_low_stock, record_analytics_event, send_receipt_email
from app.tasks.outbox_processor import process_outbox_events
from arq.connections import RedisSettings

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
