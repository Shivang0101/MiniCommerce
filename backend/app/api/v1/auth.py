from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_access_token
from app.models.user import ROLE_SCOPES, User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.services.token_blacklist import TokenBlacklistService
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await AuthService.register_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate_user(db, user_in.email, user_in.password)
    user_role = getattr(user, "role", "CUSTOMER") or "CUSTOMER"
    if user.is_admin and user_role == "CUSTOMER":
        user_role = "SRE_ADMIN"
    scopes = ROLE_SCOPES.get(user_role, ROLE_SCOPES["CUSTOMER"])

    access_token = create_access_token(subject=str(user.id), scopes=scopes)
    refresh_token = create_refresh_token(subject=str(user.id))

    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        samesite="lax",
        secure=False,
    )

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/refresh", response_model=Token)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        # Fallback to Authorization header if cookie not provided
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            refresh_token = auth_header.split(" ")[1]

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )

    payload = decode_access_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    jti = payload.get("jti")
    if jti and await TokenBlacklistService.is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been revoked"
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject"
        )

    import uuid

    user = await AuthService.get_user_by_id(db, uuid.UUID(sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists"
        )

    # Blacklist used refresh token (rotation)
    if jti:
        await TokenBlacklistService.revoke_token(
            jti, ttl_seconds=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        )

    user_role = getattr(user, "role", "CUSTOMER") or "CUSTOMER"
    if user.is_admin and user_role == "CUSTOMER":
        user_role = "SRE_ADMIN"
    scopes = ROLE_SCOPES.get(user_role, ROLE_SCOPES["CUSTOMER"])

    new_access_token = create_access_token(subject=str(user.id), scopes=scopes)
    new_refresh_token = create_refresh_token(subject=str(user.id))

    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=new_refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        samesite="lax",
        secure=False,
    )

    return Token(
        access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer"
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response, request: Request, current_user: User = Depends(get_current_user)
):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        if payload and payload.get("jti"):
            await TokenBlacklistService.revoke_token(
                payload["jti"], ttl_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if refresh_token:
        r_payload = decode_access_token(refresh_token)
        if r_payload and r_payload.get("jti"):
            await TokenBlacklistService.revoke_token(
                r_payload["jti"], ttl_seconds=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
            )

    response.delete_cookie(key=settings.REFRESH_COOKIE_NAME)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
