import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class ProductCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    price: Decimal = Field(..., ge=0)
    stock: int = Field(..., ge=0)

class ProductUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(None, ge=0)
    stock: int | None = Field(None, ge=0)

class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    price: Decimal
    stock: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
