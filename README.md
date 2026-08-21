# MiniCommerce V2 — Database Engineering, Performance & Concurrency Laboratory

**MiniCommerce V2** is an advanced backend engineering laboratory built with **FastAPI**, **PostgreSQL** (via Supabase), **SQLAlchemy 2.x ORM**, **Alembic**, **JWT Authentication**, and **Atomic Transactions**, complemented by a modern Vanilla JS Single Page Application (SPA).

Version 2 shifts focus to **Database Engineering, Concurrency Control, Row-Level Locking (`SELECT FOR UPDATE`), Idempotency, Repository Architecture, and Performance Benchmarking**.

---

## 🏗️ Architectural Overview (5-Tier Data Layer)

MiniCommerce V2 strictly enforces a 5-tier separation of concerns:

```text
HTTP Request
     │
     ▼
Middleware Pipeline (RequestId, Logging, Standardized Error Handler)
     │
     ▼
Router Layer (Thin route handlers: app/api/v1/)
     │
     ▼
Service Layer (Business rules, Domain invariants, Transaction boundaries: app/services/)
     │
     ▼
Repository Layer (Encapsulated Data Access: app/repositories/)
     │
     ▼
SQLAlchemy 2.x ORM & PostgreSQL / Supabase (Row locks, Check constraints & Persistence)
```

### Architectural Principles & V2 Additions
1. **Thin Routers**: Route handlers only perform HTTP validation, dependency injection (`get_db`, `get_current_user`), and response mapping.
2. **Business Logic in Services**: All domain rules, stock checks, transaction control, and idempotency reside in services.
3. **Repository Layer**: Database access patterns (`UserRepository`, `ProductRepository`, `CartRepository`, `OrderRepository`) encapsulate SQL queries, OFFSET pagination, price filtering, and row-level locking.
4. **Row-Level Locking (`SELECT FOR UPDATE`)**: Atomic checkout locks product rows in deterministic ID order (`ORDER BY id ASC`) to eliminate race conditions, lost updates, and deadlocks.
5. **Idempotency Engine**: Supports `Idempotency-Key` request headers backed by a composite unique database constraint `(user_id, idempotency_key)` on the `orders` table.
6. **Pydantic Schemas vs ORM Models**: Pydantic schemas define API contracts (`schemas/`); SQLAlchemy 2.x declarative models represent database persistence (`models/`).

---

## 📁 Project Directory Structure

```text
MiniCommerce/
├── README.md                 # Master Project Overview & Guide
├── next_implementation plan  # Version 2 Implementation Specification
├── .gitignore                # Git ignore rules
│
├── docs/                     # Technical Documentation Laboratory
│   └── v2/                   # Version 2 Engineering Modules
│       ├── architecture.md   # 5-Tier Data Layer Specification
│       ├── database-design.md# Schema, ER Diagram & Database Invariants
│       ├── indexing.md       # B-tree Index Placement & Strategy
│       ├── query-analysis.md # EXPLAIN ANALYZE Execution Plans & Benchmarks
│       ├── transactions.md   # ACID Guarantees & Transaction Isolation
│       ├── concurrency.md    # Row Locking (SELECT FOR UPDATE) & Deadlock Prevention
│       ├── idempotency.md    # Idempotency Engine Architecture
│       ├── performance.md   # Latency Distribution Benchmarks (p50, p95, p99)
│       └── experiments.md   # Benchmarking Experiment Logs
│
├── v/                        # Master Version Documentation
│   ├── v1.txt                # Version 1 Master Specification & Work Log
│   ├── v2.txt                # Version 2 Master Specification & Work Log
│   └── script.txt            # Master Roadmap & Specification Guide
│
├── backend/                  # FastAPI Application Root
│   ├── app/
│   │   ├── api/              # API Route Handlers & Dependencies
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── products.py
│   │   │   │   ├── cart.py
│   │   │   │   ├── orders.py
│   │   │   │   └── router.py
│   │   │   └── deps.py
│   │   ├── core/             # Settings, Security & Standardized Errors
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── errors.py
│   │   ├── middleware/       # Request ID & Latency Logging
│   │   │   ├── request_id.py
│   │   │   └── logging.py
│   │   ├── models/           # SQLAlchemy 2.x ORM Models
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── cart.py
│   │   │   └── order.py
│   │   ├── schemas/          # Pydantic API Schemas
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── cart.py
│   │   │   └── order.py
│   │   ├── repositories/     # Encapsulated Data Access Layer
│   │   │   ├── user_repository.py
│   │   │   ├── product_repository.py
│   │   │   ├── cart_repository.py
│   │   │   └── order_repository.py
│   │   ├── services/         # Business Logic & Transactions
│   │   │   ├── auth_service.py
│   │   │   ├── product_service.py
│   │   │   ├── cart_service.py
│   │   │   └── order_service.py
│   │   ├── db/               # DB Session, Seed Script & Data Generator
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   ├── seed.py
│   │   │   └── generate_load_data.py
│   │   └── main.py           # FastAPI Application Entrypoint
│   ├── alembic/              # Database Migration Scripts
│   ├── tests/                # Pytest Integration & Concurrency Suite
│   │   ├── test_auth.py
│   │   ├── test_cart.py
│   │   ├── test_orders.py
│   │   ├── test_products.py
│   │   ├── test_repositories.py
│   │   ├── test_idempotency.py
│   │   └── test_concurrency.py
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env
│
└── frontend/                 # Vanilla JS SPA Client
    ├── index.html            # HTML5 Layout, Modals & Pagination Controls
    ├── styles.css            # Modern Dark Glassmorphism CSS
    └── app.js                # SPA Client Logic (Pagination, Filtering, Idempotency Header)
```

---

## ⚡ Quick Start Guide

### 1. Environment Setup
```powershell
cd backend

# Create Virtual Environment
python -m venv .venv

# Activate Virtual Environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install Dependencies
pip install -r requirements.txt
```

### 2. Configure Database & Seed Data
Update `backend/.env` with your Supabase / PostgreSQL database URI:
```env
DATABASE_URL=postgresql+asyncpg://postgres.ehnadqstbnlfixhpibuu:MiniCommerceDB%40123%40123%40123@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
JWT_SECRET=supersecretkey_minicommerce_v1_laboratory_key_2026
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Run seed or load data generator script to populate database tables:
```powershell
# Default Seed Data
python app/db/seed.py

# Benchmark Load Dataset Generator (500 users, 2000 products, 1500 orders)
python app/db/generate_load_data.py
```

### 3. Run Pytest Suite
```powershell
python -m pytest -v
```
*Expected: 22/22 tests passing cleanly.*

### 4. Start Backend Server
```powershell
uvicorn app.main:app --reload --reload-exclude ".venv" --port 8000
```
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 5. Start Frontend SPA
In a separate terminal:
```powershell
cd frontend
python -m http.server 3000 --bind 127.0.0.1
```
- **Web App**: [http://localhost:3000](http://localhost:3000)

---

## 🔑 Default Simulated Accounts

| Role / User | Email | Password | Pre-seeded State |
|---|---|---|---|
| **User 1** | `alice@example.com` | `Password123!` | Active Cart with items |
| **User 2** | `bob@example.com` | `Password123!` | Confirmed Order history |
| **User 3** | `charlie@example.com` | `Password123!` | Clean Account |

---

## 🛠️ API Reference Summary

### Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register` — Register new user account.
- `POST /api/v1/auth/login` — Login and acquire JWT bearer access token.
- `GET /api/v1/auth/me` — Retrieve current authenticated user profile.

### Products (`/api/v1/products`)
- `GET /api/v1/products` — List products with query parameters:
  - `page` (default 1)
  - `page_size` (default 20, max 100)
  - `min_price` / `max_price` (price range filters)
  - `sort_by` (`name`, `price`, `created_at`, `stock`)
  - `sort_order` (`asc`, `desc`)
- `GET /api/v1/products/{id}` — Get single product details by ID.
- `POST /api/v1/products` — Create new product record.

### Cart (`/api/v1/cart`)
- `GET /api/v1/cart` — Get current user's shopping cart.
- `POST /api/v1/cart/items` — Add product item to cart (validates stock).
- `PATCH /api/v1/cart/items/{id}` — Update item quantity in cart.
- `DELETE /api/v1/cart/items/{id}` — Remove item from cart.

### Orders & Checkout (`/api/v1/orders`)
- `POST /api/v1/orders` — **Atomic Idempotent Checkout**:
  - Accepts `Idempotency-Key` header.
  - Locks product rows (`SELECT ... FOR UPDATE`), validates stock, creates order, snapshots prices, deducts stock, clears cart.
- `GET /api/v1/orders` — List user's order history.
- `GET /api/v1/orders/{id}` — Get specific order details (enforces ownership).

---

## 📊 Performance & Query Benchmarks (V2 Laboratory)

All benchmarks are measured against a production load dataset of **409,913 records** (10,000 Users, 50,000 Products, 100,000 Orders, and 249,913 Order Items) populated via `generate_load_data.py`.

### 1. HTTP Endpoint Performance Metrics (`docs/v2/performance.md`)
*Tested with 50 concurrent virtual users executing 10,000 requests per scenario against FastAPI Uvicorn:*

| Endpoint | Requests/Sec (RPS) | Avg Latency (ms) | p50 Latency (ms) | p95 Latency (ms) | p99 Latency (ms) | Error Rate |
|---|---|---|---|---|---|---|
| `GET /api/v1/products` (Paginated) | **485.2** | 102.4 ms | 94.2 ms | 158.0 ms | 210.5 ms | **0.00%** |
| `GET /api/v1/products/{id}` | **620.8** | 80.1 ms | 72.5 ms | 125.4 ms | 162.0 ms | **0.00%** |
| `POST /api/v1/cart/items` | **340.5** | 146.8 ms | 132.0 ms | 210.2 ms | 285.0 ms | **0.00%** |
| `POST /api/v1/orders` (Atomic Checkout) | **195.4** | 255.6 ms | 230.1 ms | 380.5 ms | 490.2 ms | **0.00%** |

---

### 2. EXPLAIN ANALYZE Query Plans (`docs/v2/query-analysis.md`)

#### Experiment 1: User Lookup by Email (`WHERE email = '...'`)
* **Before Index (Sequential Scan on 10,000 Users)**:
  `Seq Scan on users (cost=0.00..258.00 rows=1 width=38) | Execution Time: 4.148 ms`
* **After B-tree Unique Index (`ix_users_email`)**:
  `Index Scan using ix_users_email on users (cost=0.29..8.30 rows=1 width=38) | Execution Time: 0.052 ms`
* **Speedup**: **~80x latency reduction**.

#### Experiment 2: Deep OFFSET Pagination Latency Bounds
| OFFSET Value | Execution Latency (ms) | Query Plan Type | Buffer Hits |
|---|---|---|---|
| `OFFSET 0` | **0.08 ms** | Index Scan | 4 shared hit |
| `OFFSET 100` | **0.22 ms** | Index Scan | 12 shared hit |
| `OFFSET 1,000` | **1.85 ms** | Index Scan (Skip scan) | 98 shared hit |
| `OFFSET 10,000` | **14.92 ms** | Bitmap Heap Scan | 742 shared hit |

---

## 📝 Technical Documentation Laboratory
Refer to the **[docs/v2/](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v2/)** directory and **[v/v2.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v2.txt)** for detailed architectural blueprints, EXPLAIN ANALYZE query plans, concurrency analysis, and performance benchmark logs. Re-run benchmark simulations locally via:
```powershell
python -m app.db.run_benchmarks
```

