import logging
from redis.asyncio import Redis, ConnectionPool
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_pool: ConnectionPool | None = None
redis_client: Redis | None = None


async def init_redis_pool() -> None:
    global redis_pool, redis_client
    try:
        redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.2,
            socket_timeout=0.2
        )
        redis_client = Redis(connection_pool=redis_pool)
        # Test connection ping
        await redis_client.ping()
        logger.info(f"Connected to Redis pool at {settings.REDIS_URL}")
    except Exception as e:
        redis_client = None
        redis_pool = None
        logger.warning(f"Failed to initialize Redis pool on startup: {e}. Falling back to DB-only operations.")


async def close_redis_pool() -> None:
    global redis_pool, redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None
    logger.info("Closed Redis connection pool.")


def get_redis() -> Redis | None:
    return redis_client
