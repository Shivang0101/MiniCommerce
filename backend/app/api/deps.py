import uuid

from app.core.security import decode_access_token
from app.db.session import get_db, get_read_db, get_write_db
from app.models.user import ROLE_SCOPES, User
from app.services.auth_service import AuthService
from app.services.token_blacklist import TokenBlacklistService
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ["get_db", "get_read_db", "get_write_db", "get_current_user", "get_current_admin_user", "require_scope"]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Check if token is access token type
    token_type = payload.get("type")
    if token_type and token_type != "access":
        raise credentials_exception

    jti = payload.get("jti")
    if jti:
        is_revoked = await TokenBlacklistService.is_token_revoked(jti)
        if is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

    sub: str | None = payload.get("sub")
    if sub is None:
        raise credentials_exception

    try:
        user_id = uuid.UUID(sub)
    except ValueError:
        raise credentials_exception

    user = await AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin and current_user.role != "SRE_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return current_user


def require_scope(required_scope: str):
    async def scope_dependency(current_user: User = Depends(get_current_user)) -> User:
        user_role = getattr(current_user, "role", "CUSTOMER") or "CUSTOMER"
        if current_user.is_admin and user_role == "CUSTOMER":
            user_role = "SRE_ADMIN"

        user_scopes = ROLE_SCOPES.get(user_role, ROLE_SCOPES["CUSTOMER"])
        if required_scope not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Missing required scope '{required_scope}' for role '{user_role}'",
            )
        return current_user

    return scope_dependency
