import time
import json
import logging
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("minicommerce.access")
logging.basicConfig(level=logging.INFO, format="%(message)s")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        request_id = getattr(request.state, "request_id", "N/A")
        trace_id = request.headers.get("X-Trace-ID") or f"trace_{request_id[:8]}"

        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO" if response.status_code < 400 else ("WARN" if response.status_code < 500 else "ERROR"),
            "trace_id": trace_id,
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": latency_ms
        }
        logger.info(json.dumps(log_payload))

        return response

