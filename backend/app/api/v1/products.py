import uuid
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=list[ProductResponse])
async def list_products(
    response: Response,
    page: int = Query(1, ge=1, description="Page number (>= 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (1..100)"),
    min_price: Decimal | None = Query(None, ge=0, description="Minimum price filter"),
    max_price: Decimal | None = Query(None, ge=0, description="Maximum price filter"),
    sort_by: str = Query("name", description="Field to sort by: name, price, created_at, stock"),
    sort_order: str = Query("asc", description="Sort direction: asc or desc"),
    search: str | None = Query(None, description="Search term for name or description"),
    category: str | None = Query(None, description="Category filter term"),
    db: AsyncSession = Depends(get_db)
):
    products, total_count = await ProductService.list_products(
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
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    return products

@router.get("/{id}", response_model=ProductResponse)
async def get_product(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await ProductService.get_product(db, id)

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await ProductService.create_product(db, product_in)
