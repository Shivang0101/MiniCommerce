# Redis Sliding-Window Rate Limiting Middleware

## Overview
MiniCommerce V4 incorporates a **Redis-Backed Sliding-Window Rate Limiting Middleware** (`RateLimiterMiddleware`) to protect API endpoints against burst traffic, resource exhaustion, and brute-force attempts.

---

## Algorithm Mechanics

The rate limiter employs **Redis Sorted Sets (ZSET)** to maintain precise sub-second request timestamps for each client over a rolling 60-second window.

### Pipeline Execution:
1. `ZREMRANGEBYSCORE key 0 (now - 60)` -> Purges expired request timestamps older than 60 seconds.
2. `ZADD key now now` -> Records current request timestamp.
3. `ZCARD key` -> Counts total requests executed in current window.
4. `EXPIRE key 65` -> Sets TTL to auto-cleanup key.

---

## Route Tiers & Thresholds

| Route Pattern | Tier Name | Limit (reqs / min) | Purpose |
| :--- | :--- | :--- | :--- |
| `/api/v1/auth/*` | `auth` | 10 | Protects login/register against brute-force attacks |
| `/api/v1/products` | `default` | 60 | Protects product catalog queries |
| `/api/v1/admin/*` | `admin` | 120 | Accommodates admin metrics polling |

---

## HTTP Response Specification

When request count exceeds the tier limit:
- **HTTP Status Code**: `429 Too Many Requests`
- **Headers**:
  - `Retry-After`: Seconds remaining in cooldown window (e.g. `14`).
  - `X-RateLimit-Limit`: Maximum requests allowed in tier.
  - `X-RateLimit-Remaining`: `0`.
  - `X-RateLimit-Reset`: Unix timestamp when quota resets.
- **Frontend Behavior**: Triggers live cooldown countdown modal in customer storefront (`RateLimitModal.jsx`).
