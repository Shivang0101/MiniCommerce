# Version 4 Troubleshooting & Debugging Log

This document records all errors, root causes, symptoms, and structural solutions encountered during the implementation and execution of Version 4 (Asynchronous ARQ Task Processing, Sliding-Window Rate Limiting & Admin Observability).

---

## 1. Schema Validation Error on Null Timestamps (`updated_at`)

- **Symptom**: `fastapi.exceptions.ResponseValidationError` (HTTP 500 Internal Server Error) when calling `GET /api/v1/products`.
- **Root Cause**: `ProductResponse` defined `updated_at: datetime` as required and non-nullable. Supabase PostgreSQL records for catalog products had `null` values for `updated_at`.
- **Solution**:
  - Updated `app/schemas/product.py` to make `created_at` and `updated_at` optional (`datetime | None = None`).
  - Updated catalog serialization in `app/services/product_service.py` to handle `null` timestamp values during Redis caching.

---

## 2. Missing Database Column (`users.is_admin`)

- **Symptom**: `sqlalchemy.exc.ProgrammingError: column users.is_admin does not exist` during `/auth/login` and `/auth/register`.
- **Root Cause**: `Base.metadata.create_all` creates newly added tables, but does not alter pre-existing PostgreSQL tables created in V1-V3.
- **Solution**:
  - Added migration statement `ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;` to `app/db/migrate_idempotency.py`.
  - Added automatic column migration execution to FastAPI's `lifespan` startup context in `app/main.py`.

---

## 3. Pre-existing Admin Accounts Flagged as Non-Admin

- **Symptom**: Logging in as `admin@minicommerce.com` returned `is_admin: false`, preventing access to the Admin Dashboard.
- **Root Cause**: When the `is_admin` column was added to PostgreSQL, pre-existing user records received `FALSE` by default. `seed.py` skipped existing users without updating properties.
- **Solution**:
  - Executed `UPDATE users SET is_admin = TRUE WHERE email = 'admin@minicommerce.com';` via `app/db/promote_admin.py`.
  - Updated `app/db/seed.py` so existing seed users automatically get their `is_admin` and password properties refreshed.

---

## 4. Frontend Admin Dashboard Login Form Re-rendering Post-Auth

- **Symptom**: Clicking "Authenticate as Admin" in the UI authenticated the backend session, but did not navigate to the Admin Dashboard view.
- **Root Cause**: `/auth/login` returns `{ access_token: "..." }` without a nested `user` object, leaving `res.data.user` as `undefined` until `/auth/me` is called.
- **Solution**:
  - Updated `handleAdminLogin` in `AdminDashboard.jsx` to fetch `GET /auth/me` immediately after `/auth/login` and store the complete `userProfile`.
  - Added automatic token validation on component mount (`useEffect`) in `AdminDashboard.jsx`.

---

## 5. Simulated Delays in Benchmark Comparison (`run_benchmarks.py`)

- **Symptom**: V4 async checkout benchmark baseline relied on hardcoded `time.sleep()` calls.
- **Root Cause**: Baseline comparison required a synchronous model representation after `OrderService` was refactored for ARQ async task offloading.
- **Solution**:
  - Refactored `run_v4_async_checkout_benchmarks` in `app/db/run_benchmarks.py` to run real task functions inline vs ARQ Redis job enqueuing for 100% empirical, zero-sleep measurements.

---

## 6. Docker Container Code Hot Reloading & Nginx Asset Caching

- **Symptom**: Backend code edits did not reflect in running containers immediately, and Nginx served cached compiled Vite JS bundles.
- **Root Cause**: Missing volume mounts for `./backend` in `docker-compose.yml`, and Nginx serving static compiled assets built at Docker image creation.
- **Solution**:
  - Added `volumes: - ./backend:/app` to `docker-compose.yml` for instant backend hot-reloading.
  - Documented `docker-compose up --build` for frontend static asset compilation.

---

## 7. Vite Dev Proxy `ECONNREFUSED` Startup Log (`127.0.0.1:8000`)

- **Symptom**: Terminal output `[vite] http proxy error: /api/v1/admin/metrics Error: connect ECONNREFUSED 127.0.0.1:8000` when running `npm run dev`.
- **Root Cause**: Vite dev server initializes in ~1.6s and immediately starts polling backend telemetry endpoints before Uvicorn completes its database lifespan initialization on port 8000.
- **Solution**:
  - Once Uvicorn finishes binding to port 8000 (after ~2s), subsequent API calls succeed automatically.
  - For production execution, `docker-compose up` handles service startup ordering via container healthchecks.
