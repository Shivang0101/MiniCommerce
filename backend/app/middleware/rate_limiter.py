import logging
import time

from app.core.config import settings
from app.core.redis import get_redis
from app.core.security import decode_access_token
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude documentation, OpenAPI schema, and health probes from rate limiting
        path = request.url.path
        if path in [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/",
            "/healthz",
            "/readyz",
        ] or path.startswith("/assets/"):
            return await call_next(request)

        redis = get_redis()
        # If Redis is unavailable, log warning and bypass rate limiter gracefully
        if not redis:
            return await call_next(request)

        # 1. Identify Client (Authenticated User ID or IP)
        client_id = request.client.host if request.client else "127.0.0.1"
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            if payload and "sub" in payload:
                client_id = f"user:{payload['sub']}"

        # 2. Determine Route Tier & Threshold
        if path.startswith("/api/v1/auth"):
            tier_name = "auth"
            limit = settings.RATE_LIMIT_AUTH
        elif path.startswith("/api/v1/admin"):
            tier_name = "admin"
            limit = settings.RATE_LIMIT_ADMIN
        else:
            tier_name = "default"
            limit = settings.RATE_LIMIT_DEFAULT

        # 3. Redis Sliding Window (60 seconds)
        window_seconds = 60
        now = time.time()
        clear_before = now - window_seconds
        key = f"rate_limit:{client_id}:{tier_name}"

        try:
            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, clear_before)
            pipe.zadd(key, {f"{now}": now})
            pipe.zcard(key)
            pipe.expire(key, window_seconds + 5)
            results = await pipe.execute()

            request_count = results[2]
            remaining = max(0, limit - request_count)

            # Record active user timestamp if client is an authenticated user
            if client_id.startswith("user:"):
                user_uuid = client_id.replace("user:", "")
                await redis.zadd("active_users", {user_uuid: now})

            if request_count > limit:
                logger.warning(
                    f"Rate limit exceeded for client '{client_id}' on path '{path}' ({request_count}/{limit})"
                )
                retry_after = 14  # estimated window cooldown
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Too Many Requests",
                        "detail": f"Rate limit exceeded ({limit} requests per minute). Please try again in {retry_after} seconds.",
                        "retry_after_seconds": retry_after,
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(now + retry_after)),
                    },
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(now + window_seconds))
            return response

        except Exception as e:
            logger.warning(f"Rate limiter check failed: {e}. Falling back to normal flow.")
            return await call_next(request)
