import uuid

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from app.services.cart_service import CartService
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await CartService.get_or_create_cart(db, current_user.id)


@router.post("/items", response_model=CartResponse)
async def add_cart_item(
    item_in: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CartService.add_item(db, current_user.id, item_in)


@router.patch("/items/{id}", response_model=CartResponse)
async def update_cart_item(
    id: uuid.UUID,
    item_in: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CartService.update_item_quantity(db, current_user.id, id, item_in)


@router.delete("/items/{id}", response_model=CartResponse)
async def remove_cart_item(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CartService.remove_item(db, current_user.id, id)
