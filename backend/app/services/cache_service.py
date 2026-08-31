import json
import logging
from typing import Any

from app.core.config import settings
from app.core.redis import get_redis

logger = logging.getLogger(__name__)


class CacheService:
    @staticmethod
    async def get(key: str) -> Any | None:
        redis = get_redis()
        if not redis:
            return None
        try:
            val = await redis.get(key)
            if val:
                logger.debug(f"Cache HIT for key: {key}")
                return json.loads(val)
            logger.debug(f"Cache MISS for key: {key}")
            return None
        except Exception as e:
            logger.warning(f"Redis get failed for key '{key}': {e}. Falling back to DB.")
            return None

    @staticmethod
    async def set(key: str, value: Any, ttl: int = settings.CACHE_TTL_SECONDS) -> bool:
        redis = get_redis()
        if not redis:
            return False
        try:
            serialized = json.dumps(value)
            await redis.setex(key, ttl, serialized)
            logger.debug(f"Cache SET for key: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Redis set failed for key '{key}': {e}.")
            return False

    @staticmethod
    async def invalidate_pattern(pattern: str) -> int:
        redis = get_redis()
        if not redis:
            return 0
        deleted_count = 0
        try:
            cursor = 0
            while True:
                cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    deleted_count += await redis.delete(*keys)
                if cursor == 0:
                    break
            logger.info(f"Invalidated {deleted_count} cache keys matching pattern: '{pattern}'")
            return deleted_count
        except Exception as e:
            logger.warning(f"Redis invalidation failed for pattern '{pattern}': {e}.")
            return 0

    @staticmethod
    async def invalidate_product_cache() -> int:
        return await CacheService.invalidate_pattern("products:*")
