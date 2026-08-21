from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.deps import get_db
from app.core.redis import get_redis

health_router = APIRouter(tags=["Health"])


@health_router.get("/healthz", status_code=status.HTTP_200_OK)
async def liveness_probe():
    """Liveness probe to verify FastAPI process is responsive."""
    return {"status": "ok", "service": "minicommerce-backend"}


@health_router.get("/readyz")
async def readiness_probe(response: Response, db: AsyncSession = Depends(get_db)):
    """
    Readiness probe to verify active downstream connections to both:
    1. Supabase PostgreSQL database via SQLAlchemy AsyncSession
    2. Redis in-memory cache pool
    """
    db_ok = False
    redis_ok = False

    # Check Database connection
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            db_ok = True
    except Exception:
        db_ok = False

    # Check Redis connection
    try:
        redis_client = get_redis()
        if redis_client and await redis_client.ping():
            redis_ok = True
    except Exception:
        redis_ok = False

    all_healthy = db_ok and redis_ok
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    response.status_code = status_code

    return {
        "status": "ready" if all_healthy else "unready",
        "dependencies": {
            "database": "connected" if db_ok else "unreachable",
            "redis": "connected" if redis_ok else "unreachable"
        }
    }
