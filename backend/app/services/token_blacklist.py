import logging
from app.core.redis import get_redis

logger = logging.getLogger(__name__)

class TokenBlacklistService:
    @staticmethod
    async def revoke_token(jti: str, ttl_seconds: int = 86400) -> bool:
        """Stores token jti in Redis blacklist with a TTL matching token expiration."""
        redis = get_redis()
        if not redis:
            logger.warning("Redis unavailable; unable to store revoked token JTI.")
            return False
        try:
            key = f"blacklist:{jti}"
            await redis.setex(key, max(1, ttl_seconds), "revoked")
            return True
        except Exception as e:
            logger.error(f"Error blacklisting token {jti}: {e}")
            return False

    @staticmethod
    async def is_token_revoked(jti: str) -> bool:
        """Checks if a given token jti exists in the Redis blacklist."""
        redis = get_redis()
        if not redis:
            return False
        try:
            key = f"blacklist:{jti}"
            exists = await redis.exists(key)
            return exists > 0
        except Exception as e:
            logger.error(f"Error checking token blacklist for {jti}: {e}")
            return False
