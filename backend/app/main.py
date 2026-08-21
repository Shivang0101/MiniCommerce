from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_v1_router
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.core.errors import api_exception_handler
from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base

from app.core.redis import init_redis_pool, close_redis_pool
from app.api.v1.health import health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database schema and Redis/ARQ pools on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;"))
        await conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(255);"))
    await init_redis_pool()
    yield
    await close_redis_pool()

app = FastAPI(
    title="MiniCommerce V4 Laboratory",
    description="Asynchronous Task Processing, Redis Rate Limiting & Observability Laboratory",
    version="4.0.0",
    lifespan=lifespan
)

# Exception handlers
app.add_exception_handler(HTTPException, api_exception_handler)

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
    return {"name": "MiniCommerce V4 Laboratory API", "version": "4.0.0", "status": "running", "docs": "/docs"}
