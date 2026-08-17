import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.product import Product
from app.schemas.product import ProductCreate

class ProductService:
    @staticmethod
    async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
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
    async def get_product(db: AsyncSession, product_id: uuid.UUID) -> Product:
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product

    @staticmethod
    async def list_products(db: AsyncSession) -> list[Product]:
        result = await db.execute(select(Product).order_by(Product.name))
        return list(result.scalars().all())
