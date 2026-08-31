import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from app.models.base import Base
from sqlalchemy import UUID, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.order import Order

ROLE_SCOPES = {
    "CUSTOMER": ["products:read", "cart:manage", "orders:create", "orders:read"],
    "STORE_MANAGER": [
        "products:read",
        "cart:manage",
        "orders:create",
        "orders:read",
        "products:write",
        "products:delete",
        "stock:update",
    ],
    "SRE_ADMIN": [
        "products:read",
        "cart:manage",
        "orders:create",
        "orders:read",
        "products:write",
        "products:delete",
        "stock:update",
        "admin:telemetry",
        "admin:users",
    ],
}


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="CUSTOMER", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    cart: Mapped["Cart"] = relationship(
        "Cart", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan"
    )
