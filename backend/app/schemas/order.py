import uuid
from datetime import datetime
from decimal import Decimal

from app.schemas.product import ProductResponse
from pydantic import BaseModel, ConfigDict


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    price: Decimal
    product: ProductResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_amount: Decimal
    created_at: datetime
    order_items: list[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
