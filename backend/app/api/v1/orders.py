import uuid

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.order import OrderResponse
from app.services.order_service import OrderService
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def checkout(
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await OrderService.create_order_checkout(
        db, current_user.id, idempotency_key=idempotency_key
    )


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await OrderService.get_user_orders(db, current_user.id)


@router.get("/{id}/status")
async def get_order_status(id: uuid.UUID, current_user: User = Depends(get_current_user)):
    """Poll real-time order processing status from Redis worker state."""
    import json

    from app.core.redis import get_redis

    redis = get_redis()
    if redis:
        try:
            val = await redis.get(f"order_status:{id}")
            if val:
                return json.loads(val)
        except Exception:
            pass
    return {"status": "Confirmed", "detail": "Order confirmed and stored in database."}


@router.get("/{id}", response_model=OrderResponse)
async def get_order(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await OrderService.get_user_order_by_id(db, current_user.id, id)
