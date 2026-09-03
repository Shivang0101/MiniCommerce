import logging
from contextlib import asynccontextmanager

from app.api.v1.health import health_router
from app.api.v1.router import api_v1_router
from app.core.errors import api_exception_handler
from app.core.redis import close_redis_pool, init_redis_pool
from app.core.telemetry import setup_telemetry
from app.db.base import Base
from app.db.session import engine
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.request_id import RequestIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database schema and V5 runtime column migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if engine.dialect.name == "postgresql":
            migrations = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'CUSTOMER';",
                "ALTER TABLE orders ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(255);",
                "ALTER TABLE orders ADD COLUMN IF NOT EXISTS payload_hash VARCHAR(255);",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;",
                "ALTER TABLE outbox ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0;",
                "ALTER TABLE outbox ADD COLUMN IF NOT EXISTS max_retries INTEGER NOT NULL DEFAULT 3;",
                "ALTER TABLE outbox ADD COLUMN IF NOT EXISTS last_error TEXT;",
            ]
            for stmt in migrations:
                try:
                    await conn.execute(text(stmt))
                except Exception as e:
                    logger.warning(f"Migration statement ignored: {e}")

    await init_redis_pool()
    logger.info("MiniCommerce V5 Laboratory Backend initialized successfully.")
    yield
    logger.info(
        "Initiating graceful shutdown sequence: draining connection pools and closing resources..."
    )
    await close_redis_pool()
    await engine.dispose()
    logger.info("Graceful shutdown complete.")


app = FastAPI(
    title="MiniCommerce V8 Laboratory",
    description="Enterprise Observability, Site Reliability Engineering & Cloud Architecture Laboratory",
    version="8.0.0",
    lifespan=lifespan,
)

# Setup Prometheus metrics exporter and OpenTelemetry tracing
setup_telemetry(app)


# Exception handlers
app.add_exception_handler(HTTPException, api_exception_handler)  # type: ignore[arg-type]

# Custom Middlewares
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIdMiddleware)

# CORS configuration (Added last so it wraps all middlewares and exception handlers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "name": "MiniCommerce V4 Laboratory API",
        "version": "4.0.0",
        "status": "running",
        "docs": "/docs",
    }
