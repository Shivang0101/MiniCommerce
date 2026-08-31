import logging

from app.core.config import settings
from arq.connections import ArqRedis, RedisSettings, create_pool
from redis.asyncio import ConnectionPool, Redis

logger = logging.getLogger(__name__)

redis_pool: ConnectionPool | None = None
redis_client: Redis | None = None
arq_pool: ArqRedis | None = None


async def init_redis_pool() -> None:
    global redis_pool, redis_client, arq_pool
    try:
        redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
        redis_client = Redis(connection_pool=redis_pool)
        # Test connection ping
        await redis_client.ping()
        logger.info(f"Connected to Redis pool at {settings.REDIS_URL}")
    except Exception as e:
        redis_client = None
        redis_pool = None
        logger.warning(
            f"Failed to initialize Redis pool on startup: {e}. Falling back to DB-only operations."
        )

    try:
        arq_settings = RedisSettings.from_dsn(settings.REDIS_URL)
        arq_pool = await create_pool(arq_settings)
        logger.info(f"Connected to ARQ Redis queue pool at {settings.REDIS_URL}")
    except Exception as e:
        arq_pool = None
        logger.warning(
            f"Failed to initialize ARQ pool on startup: {e}. Task offloading will fall back gracefully."
        )


async def close_redis_pool() -> None:
    global redis_pool, redis_client, arq_pool
    if arq_pool:
        await arq_pool.close()
        arq_pool = None
        logger.info("Closed ARQ connection pool.")
    if redis_client:
        await redis_client.aclose()
        redis_client = None
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None
    logger.info("Closed Redis connection pool.")


def get_redis() -> Redis | None:
    return redis_client


def get_arq_pool() -> ArqRedis | None:
    return arq_pool
