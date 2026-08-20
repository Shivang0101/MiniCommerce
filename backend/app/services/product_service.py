import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.product import Product
from app.schemas.product import ProductCreate
from app.repositories.product_repository import ProductRepository

class ProductService:
    @staticmethod
    async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
        return await ProductRepository.create(db, product_in)

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
        sort_order: str = "asc"
    ) -> list[Product]:
        products, total_count = await ProductRepository.list_products(
            db,
            page=page,
            page_size=page_size,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return products
