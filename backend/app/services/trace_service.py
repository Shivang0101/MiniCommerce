import json
import logging
import time
from typing import Any

from app.core.redis import get_redis

logger = logging.getLogger(__name__)


class TraceService:
    @staticmethod
    async def record_trace(
        trace_id: str, endpoint: str, total_duration_ms: float, spans: list[dict[str, Any]]
    ) -> None:
        redis = get_redis()
        if not redis:
            return
        try:
            trace_data = {
                "trace_id": trace_id,
                "endpoint": endpoint,
                "timestamp": time.time(),
                "total_duration_ms": round(total_duration_ms, 2),
                "spans": spans,
            }
            # Store individual trace payload (TTL 1 hour)
            await redis.setex(f"trace:{trace_id}", 3600, json.dumps(trace_data))
            # Push to recent traces list (capped at 50)
            await redis.lpush("recent_traces", json.dumps(trace_data))
            await redis.ltrim("recent_traces", 0, 49)
        except Exception as e:
            logger.warning(f"Failed to record trace {trace_id}: {e}")

    @staticmethod
    async def get_trace(trace_id: str) -> dict[str, Any] | None:
        redis = get_redis()
        if not redis:
            return None
        try:
            raw = await redis.get(f"trace:{trace_id}")
            return json.loads(raw) if raw else None
        except Exception as e:
            logger.warning(f"Failed to fetch trace {trace_id}: {e}")
            return None

    @staticmethod
    async def list_recent_traces(limit: int = 20) -> list[dict[str, Any]]:
        redis = get_redis()
        if not redis:
            return []
        try:
            items = await redis.lrange("recent_traces", 0, limit - 1)
            return [json.loads(item) for item in items]
        except Exception as e:
            logger.warning(f"Failed to list recent traces: {e}")
            return []
