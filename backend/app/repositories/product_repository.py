import uuid
from decimal import Decimal
from typing import Sequence
from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.schemas.product import ProductCreate

class ProductRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, product_id: uuid.UUID) -> Product | None:
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_products(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> tuple[list[Product], int]:
        stmt = select(Product)

        # Apply price filters
        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)

        # Count total matching rows
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total_count = total_result.scalar_one() or 0

        # Whitelist allowed sort fields
        valid_sort_fields = {
            "name": Product.name,
            "price": Product.price,
            "created_at": Product.created_at,
            "stock": Product.stock
        }
        sort_column = valid_sort_fields.get(sort_by.lower(), Product.name)
        direction = desc if sort_order.lower() == "desc" else asc

        stmt = stmt.order_by(direction(sort_column))

        # OFFSET pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await db.execute(stmt)
        products = list(result.scalars().all())

        return products, total_count

    @staticmethod
    async def get_by_ids_for_update(db: AsyncSession, product_ids: list[uuid.UUID]) -> list[Product]:
        """
        Fetch products by IDs using row-level locking (SELECT ... FOR UPDATE).
        Orders by Product.id ASC deterministically to prevent deadlocks during concurrent checkouts.
        """
        if not product_ids:
            return []
        
        # Sort IDs to enforce deterministic locking order
        sorted_ids = sorted(product_ids)

        stmt = (
            select(Product)
            .where(Product.id.in_(sorted_ids))
            .order_by(Product.id.asc())
            .with_for_update()
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, product_in: ProductCreate) -> Product:
        product = Product(
            name=product_in.name,
            description=product_in.description,
            price=product_in.price,
            stock=product_in.stock
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def update_stock_atomic(db: AsyncSession, product_id: uuid.UUID, quantity: int) -> bool:
        """
        Atomic update: UPDATE products SET stock = stock - quantity WHERE id = product_id AND stock >= quantity
        """
        product = await ProductRepository.get_by_id(db, product_id)
        if not product or product.stock < quantity:
            return False
        product.stock -= quantity
        return True
