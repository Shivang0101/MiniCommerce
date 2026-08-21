# 🔐 MiniCommerce V5 Documentation — Zero-Trust Security, Token Rotation & Scoped RBAC

Version 5 introduces Enterprise Zero-Trust Security to MiniCommerce, decoupling long-lived session persistence from short-lived API authorization, providing instant token revocation, and enforcing fine-grained Role-Based Access Control (RBAC).

---

## 🔑 1. Dual-Token Authentication System

MiniCommerce V5 transitions from single long-lived access tokens to a **Dual-Token System**:

| Token Type | Lifespan | Delivery Mechanism | Purpose |
|---|---|---|---|
| **Access Token** | 15 Minutes | `Authorization: Bearer <token>` Header | Short-lived endpoint authorization carrying `jti` (JWT ID), user ID (`sub`), type `"access"`, and scope list (`scopes`). |
| **Refresh Token** | 7 Days | `HttpOnly`, `SameSite=Lax` Cookie | Long-lived session token used strictly to rotate tokens via `POST /api/v1/auth/refresh`. |

### Token Rotation Flow (`POST /api/v1/auth/refresh`)
1. Client sends request to `/api/v1/auth/refresh` containing the `refresh_token` cookie.
2. Backend decodes refresh token, verifies token type is `"refresh"`, and checks if `jti` is revoked in Redis.
3. Backend revokes the old refresh token `jti` in Redis (`blacklist:{jti}`).
4. Backend issues a **new Access Token** and sets a **new rotated Refresh Token cookie**.

---

## 🚫 2. Redis Token Revocation List (`TokenBlacklistService`)

When users log out or tokens are rotated, JWTs are revoked instantly using Redis:

```python
class TokenBlacklistService:
    @staticmethod
    async def revoke_token(jti: str, ttl_seconds: int = 86400) -> bool:
        redis = get_redis()
        if not redis:
            return False
        key = f"blacklist:{jti}"
        await redis.setex(key, max(1, ttl_seconds), "revoked")
        return True
```

### Logout Protocol (`POST /api/v1/auth/logout`)
- Extracts `jti` from current Access Token and Refresh Token cookie.
- Stores `blacklist:{jti}` in Redis with TTL matching token expiration.
- Clears `refresh_token` cookie in the HTTP response.
- `deps.get_current_user` intercepts every request and checks `TokenBlacklistService.is_token_revoked(jti)`. If revoked, returns `HTTP 401 Unauthorized`.

---

## 🛡️ 3. Scoped Role-Based Access Control (RBAC)

User accounts are assigned roles mapped to explicit permission scope lists:

```python
ROLE_SCOPES = {
    "CUSTOMER": ["products:read", "cart:manage", "orders:create", "orders:read"],
    "STORE_MANAGER": [
        "products:read", "cart:manage", "orders:create", "orders:read",
        "products:write", "products:delete", "stock:update"
    ],
    "SRE_ADMIN": [
        "products:read", "cart:manage", "orders:create", "orders:read",
        "products:write", "products:delete", "stock:update",
        "admin:telemetry", "admin:users"
    ],
}
```

### Scope Dependency Enforcer (`deps.require_scope`)
Endpoints require explicit scope dependencies:

```python
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    _user = Depends(require_scope("products:delete"))
):
    ...
```

If a user with role `CUSTOMER` attempts to call `DELETE /api/v1/products/{id}`, `require_scope("products:delete")` raises `HTTP 403 Forbidden: Missing required scope 'products:delete' for role 'CUSTOMER'`.
