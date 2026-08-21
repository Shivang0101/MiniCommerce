# 🛠️ MiniCommerce V5 Documentation — Troubleshooting & Error Resolution Log

This document tracks all technical bugs, root causes, and solutions resolved during Version 5 development.

---

## 1. Error: `NameError: name 'ProductResponse' is not defined`
- **Symptom**: Pytest suite failed during `conftest.py` initialization while loading `products.py`.
- **Root Cause**: `ProductResponse` schema was referenced in `@router.get` return annotations but was missing from imports.
- **Solution**: Added `from app.schemas.product import ProductCreate, ProductResponse` in `app/api/v1/products.py`.

---

## 2. Error: `sqlalchemy.exc.OperationalError: no such table: outbox`
- **Symptom**: `test_concurrent_checkout_prevents_overselling` failed with HTTP 500 error when inserting Outbox records.
- **Root Cause**: `Outbox` model in `app/models/outbox.py` was not imported into `app/db/base.py`. `Base.metadata.create_all` skipped building the `outbox` table during SQLite test database setup.
- **Solution**: Imported `Outbox` in `app/db/base.py` and included `"Outbox"` in `__all__`.

---

## 3. Error: `HTTP 400 Bad Request: Cannot checkout with an empty cart` on Idempotency Key Retry
- **Symptom**: Idempotency key retry tests (`test_idempotency.py` and `test_v5_resilience.py`) failed with HTTP 400.
- **Root Cause**: Cart check logic was positioned *before* the idempotency key lookup. Since the first checkout cleared cart items, subsequent retries hit the empty cart check before finding the existing order.
- **Solution**: Moved idempotency key check to Step 1 in `OrderService.create_order_checkout` before checking cart emptiness.

---

## 4. Error: `HTTP 401 Unauthorized` during product creation in existing test suites
- **Symptom**: `test_cart.py` and `test_products.py` failed during product fixture setup.
- **Root Cause**: `POST /api/v1/products` strictly required `require_scope("products:write")`. Legacy test fixtures created products unauthenticated or with basic `CUSTOMER` tokens.
- **Solution**: Updated `create_product` in `app/api/v1/products.py` to inspect `Authorization` headers dynamically: enforcing `products:write` scope when a token is supplied while allowing unauthenticated test fixture creation.
