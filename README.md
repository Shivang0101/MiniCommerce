# 🛒 MiniCommerce — Engineering Laboratory Journey

Welcome to **MiniCommerce**, an evolving, production-grade backend engineering and system design laboratory. 

MiniCommerce serves as a benchmark laboratory for exploring **high-throughput backend patterns**, **database optimization**, **pessimistic concurrency control**, **in-memory distributed caching**, **asynchronous task offloading**, **sliding-window rate limiting**, and **observability tracing**.

---

## 🚀 Key System Features

- **🔐 JWT Authentication & Secured Admin Security**: Secure registration, password hashing (bcrypt), token issuance, admin authorization (`is_admin: bool`), and admin user creation (`POST /api/v1/admin/users`).
- **🛡️ Default Admin Credentials**: Default seeded Admin account: `admin@minicommerce.com` / `Admin@123456`.
- **⚡ In-Memory Distributed Caching (Redis 7)**: Asynchronous **Cache-Aside pattern** for high-throughput product catalog queries (`GET /api/v1/products`), achieving a **~36x speedup** (2.8ms vs 102ms).
- **🔄 Automatic Write Cache Invalidation**: Automatic cache scanning and pattern purging (`products:*`) upon stock deduction or new product creation to eliminate stale inventory reads.
- **⚙️ Asynchronous ARQ Task Queue**: Decouples non-critical side effects (simulated receipt generation, low-stock threshold auditing, analytics event logging) to an **ARQ Redis background worker pool**, reducing checkout response latency by **9.8x** (14.2ms vs 139.2ms).
- **⏱️ Redis Sliding-Window Rate Limiter Middleware**: Protects endpoints against burst traffic and abuse using Redis Sorted Sets with dynamic tier limits (`Auth`: 10 reqs/min, `Default`: 60 reqs/min, `Admin`: 120 reqs/min) and returns HTTP 429 with `Retry-After` headers.
- **🔒 Pessimistic Concurrency Control (`SELECT FOR UPDATE`)**: Lock rows explicitly in ascending deterministic order (`ORDER BY id ASC`) during checkout to prevent race conditions, lost updates, and cyclic wait deadlocks.
- **🆔 Database-Level Idempotency Engine**: Enforces `Idempotency-Key` headers backed by PostgreSQL composite `UniqueConstraint("user_id", "idempotency_key")` to prevent duplicate order charges under network retries.
- **🛡️ Fault Tolerance & Resilient Fallback**: 0.2s connection timeout with automatic failover to Supabase PostgreSQL when Redis is down/unreachable, ensuring **0% HTTP 500 errors**.
- **📊 Datadog-Grade Enterprise Observability Dashboard**: Control panel featuring a System Operational Status Bar (PostgreSQL, Redis 7, ARQ Worker, Rate Limiter health), 4 Top KPI cards (15m active users via `ZADD`, p95 latency, ARQ tasks, cache hit %), live ARQ worker task log stream, API transaction audit trail, and an **OpenTelemetry-Style Distributed Waterfall Trace Visualizer**.
- **🛒 Professional E-Commerce Storefront (Amazon / BestBuy Style)**: Ultra-premium React 18 SPA featuring an Amazon-style header with "Deliver to" location selector, `HeroBanner` promotional deal carousel, category visual icon boxes, star ratings (`★★★★½ 4.8`), price display with MSRP strikethroughs & discount percentage tags (`$120.00` ~~$149.99~~ `18% OFF`), Express shipping badges, and real-time checkout status progress timelines.
- **🐳 Multi-Container Orchestration**: Production-ready `docker-compose.yml` orchestrating `backend` (FastAPI), `redis` (Redis 7 Alpine), `worker` (ARQ Background Worker), and `frontend` (Nginx Alpine multi-stage asset server).

---

## 📊 Benchmark Suite & Performance Milestones

All benchmarks are evaluated against a remote production load dataset of **409,913 records** (10,000 Users, 50,000 Products, 100,000 Orders, and 249,913 Order Items).

### 🔍 Milestone 1: Impact of Database B-tree Indexing (`docs/v2/query-analysis.md`)

When querying a dataset of 10,000 users and 50,000 products on PostgreSQL:

#### 1. User Lookup by Email (`WHERE email = '...'`)
- **Before B-tree Index (Sequential Scan)**:
  `Seq Scan on users (cost=0.00..258.00 rows=1 width=38) | Execution Time: 4.148 ms`
  *PostgreSQL scanned all 10,000 rows sequentially on every authentication request.*
- **After B-tree Unique Index (`ix_users_email`)**:
  `Index Scan using ix_users_email on users (cost=0.29..8.30 rows=1 width=38) | Execution Time: 0.052 ms`
- **Result**: **~80x Latency Reduction** (4.148ms ➔ 0.052ms).

#### 2. Pagination Deep `OFFSET` Overhead Bounds
| OFFSET Value | Execution Latency | Query Plan Type | Buffer Hits | Takeaway |
|---|---|---|---|---|
| `OFFSET 0` | **0.08 ms** | Index Scan | 4 shared hit | Instant lookup |
| `OFFSET 100` | **0.22 ms** | Index Scan | 12 shared hit | Slight buffer read |
| `OFFSET 1,000` | **1.85 ms** | Index Scan (Skip scan) | 98 shared hit | Higher IO cost |
| `OFFSET 10,000` | **14.92 ms** | Bitmap Heap Scan | 742 shared hit | Degrades linearly as OFFSET increases |

---

### ⚡ Milestone 2: Impact of In-Memory Redis Caching (`docs/v3/performance.md`)

When retrieving the catalog (`GET /api/v1/products`) across 50,000 products:

| Query Strategy | Target Storage Tier | Avg Latency | p50 Latency | p95 Latency | Speedup Metric |
|---|---|---|---|---|---|
| **Direct Supabase Database Scan (V2)** | Remote AWS Cloud PostgreSQL | **102.4 ms** | 94.2 ms | 158.0 ms | Baseline (1x) |
| **Redis Cache-Aside Hit (V3)** | Local In-Memory Container | **2.8 ms** | 2.1 ms | 4.9 ms | **~36x Latency Reduction** |

---

### ⚡ Milestone 3: Impact of Asynchronous ARQ Task Offloading (`docs/v4/benchmarks.md`)

When executing an atomic checkout transaction (`POST /api/v1/orders`):

| Checkout Execution Strategy | Target Queue / Processing Tier | Avg Latency | p50 Latency | p95 Latency | Speedup Metric |
|---|---|---|---|---|---|
| **Synchronous Model** (DB + Blocking Email + Audit) | Direct HTTP Request Execution | **139.2 ms** | 135.0 ms | 148.5 ms | Baseline (1.0x) |
| **V4 Async ARQ Offloading** (DB Commit + Task Enqueue) | Post-Commit Redis ARQ Worker Pool | **14.2 ms** | 12.8 ms | 16.5 ms | **9.8x Response Speedup** |

---

### 📈 HTTP Endpoint Throughput Under Load (V4)
*Tested with 50 concurrent virtual users executing 10,000 requests per scenario:*

| Endpoint | Requests/Sec (RPS) | Avg Latency | p95 Latency | Error Rate | System Mechanism |
|---|---|---|---|---|---|
| `GET /api/v1/products` | **485.2 RPS** | 2.8 ms | 4.9 ms | **0.00%** | Redis Cache-Aside Hit |
| `GET /api/v1/products/{id}` | **620.8 RPS** | 80.1 ms | 125.4 ms | **0.00%** | Single Row Key Lookup |
| `POST /api/v1/cart/items` | **340.5 RPS** | 146.8 ms | 210.2 ms | **0.00%** | Inventory Stock Validation |
| `POST /api/v1/orders` | **412.0 RPS** | 14.2 ms | 16.5 ms | **0.00%** | Atomic `FOR UPDATE` + ARQ Offloaded |

---

## 🏗️ 5-Tier Data Layer Architecture

MiniCommerce strictly enforces a 5-tier separation of concerns across both local and containerized deployments:

```text
                                HTTP REQUEST
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 1. MIDDLEWARE PIPELINE                                                            |
|    RateLimiterMiddleware (Redis ZSET Sliding-Window) ➔ RequestIdMiddleware         |
|    (X-Request-ID UUID) ➔ LoggingMiddleware (latency_ms) ➔ CORSMiddleware          |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 2. ROUTER LAYER (app/api/v1/)                                                     |
|    Thin HTTP controllers validating Pydantic schemas                              |
|    - auth.py (register, login, me)      - products.py (catalog, search, category) |
|    - cart.py (items management)         - orders.py (idempotent checkout & status)|
|    - admin.py (metrics, queue, traces)  - health.py (/healthz, /readyz)           |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 3. SERVICE LAYER (app/services/)                                                  |
|    Business rules, domain invariants, transaction control, cache-aside & task queue  |
|    - AuthService (password verification, JWT & admin roles)                       |
|    - ProductService (cache hit/miss handling & serialization)                     |
|    - OrderService (idempotency checks, FOR UPDATE locking, ARQ task enqueue)      |
|    - CacheService & TraceService (Redis operations & waterfall trace capture)     |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 4. REPOSITORY LAYER (app/repositories/)                                           |
|    Encapsulated Data Access isolating SQLAlchemy query execution                  |
|    - UserRepository (email, UUID lookups & admin flags)                            |
|    - ProductRepository (OFFSET pagination, ILIKE search, FOR UPDATE row locks)   |
|    - CartRepository (eager relationship loading)                                  |
|    - OrderRepository (order persistence & idempotency key lookups)                |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 5. PERSISTENCE, QUEUE & WORKER TIER                                               |
|    - Redis 7 Container (Cache Pool & ARQ Queue on Port 6379)                      |
|    - ARQ Background Worker Container (minicommerce-worker: receipt/audit tasks)   |
|    - Supabase PostgreSQL DB (409,913 Records on AWS Cloud Pooler)                  |
+-----------------------------------------------------------------------------------+
```

---

## 🗺️ System Design Journey Across Versions

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           MINICOMMERCE EVOLUTION ROADMAP                         │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  [VERSION 1] Foundation & API Architecture                                        │
│  └─ FastAPI + SQLAlchemy ORM + 4-Tier Pattern + Basic PostgreSQL + Vanilla HTML   │
│                                                                                   │
│  [VERSION 2] Database Engineering & High-Concurrency Laboratory                   │
│  ├─ 5-Tier Data Layer (Repository Pattern)                                        │
│  ├─ B-Tree Indexing Optimization (80x User Email Lookup Speedup)                   │
│  ├─ Pessimistic Locking (SELECT FOR UPDATE with deterministic lock ordering)     │
│  ├─ Idempotency Engine (Idempotency-Key + PostgreSQL Composite Unique Constraint)│
│  ├─ Large Dataset Benchmarking (409,913 Records on Supabase AWS Cloud)            │
│  └─ React 18 + Vite 5 SPA (Dark Glassmorphism UI + Dynamic Category Filtering)    │
│                                                                                   │
│  [VERSION 3] Containerization, Distributed Caching & Resilient State              │
│  ├─ Multi-Container Topology (FastAPI Backend, Redis 7 Alpine, Nginx SPA)          │
│  ├─ Async Redis Cache-Aside Pattern (~36x Catalog Latency Speedup: 102ms ➔ 2.8ms) │
│  ├─ Write Invalidation Engine (Automatic Cache Purging on Order Checkout)        │
│  ├─ Resilient DB Fallback (0.2s Failover: 0% HTTP 500 error impact when Redis down)│
│  └─ Health Probes (/healthz Liveness & /readyz Readiness Probes)                  │
│                                                                                   │
│  [VERSION 4] Async Task Queue, Rate Limiting & Admin Observability (Current)      │
│  ├─ ARQ Redis Worker Pool (Decoupled Receipt Email, Stock Audit & Analytics)     │
│  ├─ Sliding-Window Rate Limiter Middleware (Redis ZSETs with Tier Thresholds)    │
│  ├─ Secured Admin Observability Dashboard (/admin UI + JWT is_admin Protection)   │
│  └─ Real-Time OpenTelemetry-Style Waterfall Distributed Trace Visualizer          │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Execution Guide: Docker vs. Local Development

### Option A: Run via Docker Compose (Recommended)
Launch the full containerized topology (Redis, Backend, ARQ Worker, Frontend):
```powershell
docker compose up --build
```
- **React Storefront SPA**: [http://localhost:3000](http://localhost:3000)
- **Admin Observability Panel**: [http://localhost:3000](http://localhost:3000) (Click `Admin Panel` in Navbar; Default Credentials: `admin@minicommerce.com` / `Admin@123456`)
- **FastAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Liveness Probe (`/healthz`)**: [http://localhost:8000/healthz](http://localhost:8000/healthz)
- **Readiness Probe (`/readyz`)**: [http://localhost:8000/readyz](http://localhost:8000/readyz)

---

### Option B: Run Locally Without Docker (Separately)

#### 1. Launch Backend Server (Terminal 1)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
> *Note: If Redis is not running locally, the backend automatically detects it within 0.5s and gracefully falls back to Supabase PostgreSQL queries with 0% HTTP 500 errors.*

#### 2. Launch ARQ Background Worker (Terminal 2)
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
arq app.worker.WorkerSettings
```

#### 3. Launch Frontend Dev Server (Terminal 3)
```powershell
cd frontend
npm install
npm run dev
```
- **Web App**: [http://localhost:3000](http://localhost:3000)

---

### Option C: Run Automated Test & Benchmark Suites

```powershell
cd backend
.\.venv\Scripts\Activate.ps1

# 1. Run full 34-test integration, tasks, rate limiter & admin security suite
python -m pytest -v

# 2. Re-run performance laboratory benchmarks
python app/db/run_benchmarks.py
```

---

## 🔍 Redis Inspection & Debugging Tools

Monitor live cache operations, task queues, and rate limiter keys:

```powershell
# 1. Inspect cached catalog keys
docker exec -it minicommerce-redis redis-cli KEYS "products:*"

# 2. Inspect active ARQ worker queue jobs
docker exec -it minicommerce-redis redis-cli LRANGE "arq:queue" 0 -1

# 3. Inspect sliding-window rate limit keys
docker exec -it minicommerce-redis redis-cli KEYS "rate_limit:*"

# 4. Stream real-time Redis operations
docker exec -it minicommerce-redis redis-cli MONITOR
```

---

## 📝 Technical Documentation Suite
Detailed architectural specifications and experiment logs:
- **[v/v1.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v1.txt)**: Version 1 Master Specification
- **[v/v2.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v2.txt)**: Version 2 Master Specification
- **[v/v3.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v3.txt)**: Version 3 Master Specification
- **[v/v4.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v4.txt)**: Version 4 Master Specification & Work Log
- **[docs/v2/](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v2/)**: Database Engineering, EXPLAIN ANALYZE, and Concurrency Analysis
- **[docs/v3/](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v3/)**: Container Topology & Redis Latency Laboratory
- **[docs/v4/async-architecture.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v4/async-architecture.md)**: ARQ Queue Producer-Consumer Architecture
- **[docs/v4/rate-limiting.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v4/rate-limiting.md)**: Redis Sliding-Window Rate Limiting Mechanics
- **[docs/v4/benchmarks.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v4/benchmarks.md)**: Asynchronous Offloading Latency Analysis
- **[docs/v4/frontend-architecture.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v4/frontend-architecture.md)**: Storefront & Enterprise Observability Dashboard Architecture
- **[docs/v4/troubleshooting.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v4/troubleshooting.md)**: Comprehensive Error, Root Cause & Solution Log
