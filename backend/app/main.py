import logging
from contextlib import asynccontextmanager

from app.api.v1.health import health_router
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.errors import api_exception_handler
from app.core.redis import close_redis_pool, init_redis_pool
from app.core.telemetry import setup_telemetry
from app.db.base import Base
from app.db.session import engine
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.request_id import RequestIdMiddleware
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# Request payload size limiter (10MB MAX)
MAX_REQUEST_BODY_SIZE = 10 * 1024 * 1024


class ContentSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_BODY_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request payload exceeds maximum allowed size (10MB)."},
            )
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database schema safely
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await init_redis_pool()
    logger.info("MiniCommerce V10 Laboratory Backend initialized successfully.")
    yield
    logger.info(
        "Initiating graceful shutdown sequence: draining connection pools and closing resources..."
    )
    await close_redis_pool()
    await engine.dispose()
    logger.info("Graceful shutdown complete.")


app = FastAPI(
    title="MiniCommerce V10 Laboratory",
    description="Enterprise Observability, Site Reliability Engineering & Cloud Architecture Laboratory",
    version="10.0.0",
    lifespan=lifespan,
)

# Setup Prometheus metrics exporter and OpenTelemetry tracing
setup_telemetry(app)


# Exception handlers
app.add_exception_handler(HTTPException, api_exception_handler)  # type: ignore[arg-type]

# Custom Middlewares
app.add_middleware(ContentSizeLimitMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIdMiddleware)

# CORS configuration with explicit origins list
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Health routes at root (/healthz, /readyz) as well as under /api/v1
app.include_router(health_router)
app.include_router(api_v1_router)


@app.get("/")
async def root():
    return {
        "name": "MiniCommerce V10 Laboratory API",
        "version": "10.0.0",
        "status": "running",
        "docs": "/docs",
    }
