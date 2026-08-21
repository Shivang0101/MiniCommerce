import uuid
from decimal import Decimal
from typing import Sequence
from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.schemas.product import ProductCreate

from datetime import datetime, timezone

class ProductRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, product_id: uuid.UUID, include_deleted: bool = False) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        if not include_deleted:
            stmt = stmt.where(Product.is_deleted == False)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_products(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        search: str | None = None,
        category: str | None = None,
        include_deleted: bool = False
    ) -> tuple[list[Product], int]:
        stmt = select(Product)
        if not include_deleted:
            stmt = stmt.where(Product.is_deleted == False)

        # Apply search and category filters
        if search:
            search_term = f"%{search.strip()}%"
            stmt = stmt.where(
                (Product.name.ilike(search_term)) | (Product.description.ilike(search_term))
            )

        if category and category.lower() != "all":
            cat_term = f"%{category.strip()}%"
            stmt = stmt.where(
                (Product.name.ilike(cat_term)) | (Product.description.ilike(cat_term))
            )

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
    async def get_products_keyset(
        db: AsyncSession,
        last_seen_id: uuid.UUID | None = None,
        limit: int = 20
    ) -> list[Product]:
        """
        Keyset (cursor-based) pagination avoiding deep OFFSET scan overhead.
        Query: SELECT * FROM products WHERE id > :last_seen_id AND is_deleted = FALSE ORDER BY id ASC LIMIT :limit
        """
        stmt = select(Product).where(Product.is_deleted == False)
        if last_seen_id:
            stmt = stmt.where(Product.id > last_seen_id)
        stmt = stmt.order_by(Product.id.asc()).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

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
            .where(Product.is_deleted == False)
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
    async def soft_delete(db: AsyncSession, product_id: uuid.UUID) -> bool:
        """Performs soft deletion (is_deleted = True, deleted_at = now()) instead of physical row deletion."""
        product = await ProductRepository.get_by_id(db, product_id, include_deleted=True)
        if not product or product.is_deleted:
            return False
        product.is_deleted = True
        product.deleted_at = datetime.now(timezone.utc)
        await db.commit()
        return True

    @staticmethod
    async def update_stock_atomic(db: AsyncSession, product_id: uuid.UUID, quantity: int) -> bool:
        product = await ProductRepository.get_by_id(db, product_id)
        if not product or product.stock < quantity:
            return False
        product.stock -= quantity
        return True

