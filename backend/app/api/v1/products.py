import uuid
from decimal import Decimal

from app.api.deps import get_db, get_read_db, require_scope
from app.core.security import decode_access_token
from app.models.user import ROLE_SCOPES
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductResponse
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.services.token_blacklist import TokenBlacklistService
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

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
    db: AsyncSession = Depends(get_read_db),
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
        category=category,
    )
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    return products


@router.get("/keyset", response_model=list[ProductResponse])
async def list_products_keyset(
    last_seen_id: uuid.UUID | None = Query(None, description="Cursor last seen product ID"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_read_db),
):
    """Keyset (cursor-based) pagination endpoint avoiding deep OFFSET performance degradation."""
    return await ProductRepository.get_products_keyset(db, last_seen_id=last_seen_id, limit=limit)


@router.get("/{id}", response_model=ProductResponse)
async def get_product(id: uuid.UUID, db: AsyncSession = Depends(get_read_db)):
    return await ProductService.get_product(db, id)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate, request: Request, db: AsyncSession = Depends(get_db)
):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        if payload:
            jti = payload.get("jti")
            if jti and await TokenBlacklistService.is_token_revoked(jti):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked"
                )
            sub = payload.get("sub")
            if sub:
                user = await AuthService.get_user_by_id(db, uuid.UUID(sub))
                if user:
                    user_role = getattr(user, "role", "CUSTOMER") or "CUSTOMER"
                    if user.is_admin and user_role == "CUSTOMER":
                        user_role = "SRE_ADMIN"
                    user_scopes = ROLE_SCOPES.get(user_role, ROLE_SCOPES["CUSTOMER"])
                    if "products:write" not in user_scopes:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden: Missing required scope 'products:write'",
                        )
    return await ProductService.create_product(db, product_in)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_scope("products:delete")),
):
    success = await ProductRepository.soft_delete(db, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or already deleted"
        )
    from app.services.cache_service import CacheService

    await CacheService.invalidate_product_cache()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
