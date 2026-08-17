import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.product import ProductResponse

class CartItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemResponse(BaseModel):
    id: uuid.UUID
    cart_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    cart_items: list[CartItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
