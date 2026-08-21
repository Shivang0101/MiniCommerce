import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.product import Product
from app.schemas.product import ProductCreate
from app.repositories.product_repository import ProductRepository

from app.services.cache_service import CacheService

class ProductService:
    @staticmethod
    async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
        product = await ProductRepository.create(db, product_in)
        await CacheService.invalidate_product_cache()
        return product

    @staticmethod
    async def get_product(db: AsyncSession, product_id: uuid.UUID) -> Product:
        product = await ProductRepository.get_by_id(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product

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
        category: str | None = None
    ) -> tuple[list[Product], int]:
        cache_key = f"products:page={page}:size={page_size}:min={min_price}:max={max_price}:sb={sort_by}:so={sort_order}:q={search}:c={category}"
        cached_data = await CacheService.get(cache_key)

        if cached_data is not None:
            # Reconstruct Product ORM instances from cached dict list
            products = [Product(**item) for item in cached_data["products"]]
            return products, cached_data["total_count"]

        products, total_count = await ProductRepository.list_products(
            db,
            page=page,
            page_size=page_size,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
            category=category
        )

        # Store serialized response in Redis cache
        serialized_products = [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "price": str(p.price),
                "stock": p.stock,
                "created_at": p.created_at.isoformat() if getattr(p, "created_at", None) else None,
                "updated_at": p.updated_at.isoformat() if getattr(p, "updated_at", None) else None,
            }
            for p in products
        ]
        await CacheService.set(cache_key, {"products": serialized_products, "total_count": total_count})
        return products, total_count
