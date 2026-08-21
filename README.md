# 🛒 MiniCommerce — Engineering Laboratory Journey

Welcome to **MiniCommerce**, an evolving, production-grade backend engineering and system design laboratory. 

MiniCommerce serves as a benchmark laboratory for exploring **high-throughput backend patterns**, **database optimization**, **pessimistic concurrency control**, **in-memory distributed caching**, and **container topology**.

---

## 🚀 Key System Features

- **🔐 JWT Authentication & User Profiles**: Secure registration, password hashing (bcrypt), token issuance, and protected profile/order history management.
- **⚡ In-Memory Distributed Caching (Redis 7)**: Asynchronous **Cache-Aside pattern** for high-throughput product catalog queries (`GET /api/v1/products`), achieving a **~36x speedup** (2.8ms vs 102ms).
- **🔄 Automatic Write Cache Invalidation**: Automatic cache scanning and pattern purging (`products:*`) upon stock deduction or new product creation to eliminate stale inventory reads.
- **🔒 Pessimistic Concurrency Control (`SELECT FOR UPDATE`)**: Lock rows explicitly in ascending deterministic order (`ORDER BY id ASC`) during checkout to prevent race conditions, lost updates, and cyclic wait deadlocks.
- **🆔 Database-Level Idempotency Engine**: Enforces `Idempotency-Key` headers backed by PostgreSQL composite `UniqueConstraint("user_id", "idempotency_key")` to prevent duplicate order charges under network retries.
- **🛡️ Fault Tolerance & Resilient Fallback**: 0.2s connection timeout with automatic failover to Supabase PostgreSQL when Redis is down/unreachable, ensuring **0% HTTP 500 errors**.
- **🩺 Distributed Health Probes**: Dedicated `/healthz` (liveness probe) and `/readyz` (readiness probe actively verifying PostgreSQL & Redis connectivity).
- **✨ Modern Glassmorphism React 18 SPA**: Responsive single-page application built with React 18, Vite 5, Tailwind CSS, Lucide Icons, interactive category chips, debounced search, and order receipt toasts.
- **🐳 Multi-Container Orchestration**: Production-ready `docker-compose.yml` orchestrating `backend` (FastAPI), `redis` (Redis 7 Alpine), and `frontend` (Nginx Alpine multi-stage asset server).

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

> **Key takeaway**: Introducing B-tree indexes reduced raw DB row scan time by **80x**, but network latency over the internet to cloud PostgreSQL remained ~100ms. Introducing Redis in-memory caching eliminated the network round-trip overhead entirely, reducing total endpoint latency to **2.8ms**.

---

### 📈 HTTP Endpoint Throughput Under Load (V3)
*Tested with 50 concurrent virtual users executing 10,000 requests per scenario:*

| Endpoint | Requests/Sec (RPS) | Avg Latency | p95 Latency | Error Rate | System Mechanism |
|---|---|---|---|---|---|
| `GET /api/v1/products` | **485.2 RPS** | 2.8 ms | 4.9 ms | **0.00%** | Redis Cache-Aside Hit |
| `GET /api/v1/products/{id}` | **620.8 RPS** | 80.1 ms | 125.4 ms | **0.00%** | Single Row Key Lookup |
| `POST /api/v1/cart/items` | **340.5 RPS** | 146.8 ms | 210.2 ms | **0.00%** | Inventory Stock Validation |
| `POST /api/v1/orders` | **195.4 RPS** | 255.6 ms | 380.5 ms | **0.00%** | Atomic `FOR UPDATE` Checkout |

---

## 🏗️ 5-Tier Data Layer Architecture

MiniCommerce strictly enforces a 5-tier separation of concerns across both local and containerized deployments:

```text
                                HTTP REQUEST
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 1. MIDDLEWARE PIPELINE                                                            |
|    RequestIdMiddleware (X-Request-ID UUID) ➔ LoggingMiddleware (latency_ms) ➔     |
|    CORSMiddleware (Outermost wrapper)                                             |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 2. ROUTER LAYER (app/api/v1/)                                                     |
|    Thin HTTP controllers validating Pydantic schemas                              |
|    - auth.py (register, login, me)      - products.py (catalog, search, category) |
|    - cart.py (items management)         - orders.py (idempotent checkout)         |
|    - health.py (/healthz, /readyz)                                                |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 3. SERVICE LAYER (app/services/)                                                  |
|    Business rules, domain invariants, transaction control, cache-aside logic      |
|    - AuthService (password verification & JWT issuance)                           |
|    - ProductService (cache hit/miss handling & serialization)                     |
|    - CartService (stock checks & item quantity rules)                             |
|    - OrderService (idempotency checks, FOR UPDATE locking, transaction commits)   |
|    - CacheService (Redis GET/SET/Invalidate pattern operations)                   |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 4. REPOSITORY LAYER (app/repositories/)                                           |
|    Encapsulated Data Access isolating SQLAlchemy query execution                  |
|    - UserRepository (email & UUID lookups)                                        |
|    - ProductRepository (OFFSET pagination, ILIKE search, FOR UPDATE row locks)   |
|    - CartRepository (eager relationship loading)                                  |
|    - OrderRepository (order persistence & idempotency key lookups)                |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 5. PERSISTENCE & CACHING TIER                                                     |
|    - Redis 7 Container (In-Memory Cache Pool on Port 6379)                        |
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
│  [VERSION 3] Containerization, Distributed Caching & Resilient State (Current)    │
│  ├─ Multi-Container Topology (FastAPI Backend, Redis 7 Alpine, Nginx SPA)          │
│  ├─ Async Redis Cache-Aside Pattern (~36x Catalog Latency Speedup: 102ms ➔ 2.8ms) │
│  ├─ Write Invalidation Engine (Automatic Cache Purging on Order Checkout)        │
│  ├─ Resilient DB Fallback (0.2s Failover: 0% HTTP 500 error impact when Redis down)│
│  └─ Health Probes (/healthz Liveness & /readyz Readiness Probes)                  │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Execution Guide: Docker vs. Local Development

### Option A: Run via Docker Compose (Recommended)
Launch the entire containerized topology with a single command:
```powershell
docker compose up --build
```
- **React Frontend**: [http://localhost:3000](http://localhost:3000)
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
> *Note: If Redis is not running locally, the backend automatically detects it within 0.2s and gracefully falls back to Supabase PostgreSQL queries with 0% HTTP 500 errors.*

#### 2. Launch Frontend Dev Server (Terminal 2)
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

# 1. Run full 27-test integration & concurrency suite
python -m pytest -v

# 2. Re-run performance laboratory benchmarks
python -m app.db.run_benchmarks
```

---

## 🔍 Redis Inspection & Debugging Tools

Monitor live cache operations while browsing or placing orders on the frontend:

```powershell
# 1. Inspect cached catalog keys
docker exec -it minicommerce-redis redis-cli KEYS "products:*"

# 2. View JSON payload of a cached page
docker exec -it minicommerce-redis redis-cli GET "products:page=1:size=12:min=None:max=None:sb=name:so=asc:q=None:c=None"

# 3. View key Time-To-Live (TTL in seconds)
docker exec -it minicommerce-redis redis-cli TTL "products:page=1:size=12:min=None:max=None:sb=name:so=asc:q=None:c=None"

# 4. Stream real-time Redis operations
docker exec -it minicommerce-redis redis-cli MONITOR
```

---

## 📝 Technical Documentation Suite
Detailed architectural specifications and experiment logs:
- **[v/v1.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v1.txt)**: Version 1 Master Specification
- **[v/v2.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v2.txt)**: Version 2 Database Engineering Specification
- **[v/v3.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v3.txt)**: Version 3 Containerization & Caching Specification
- **[docs/v2/](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v2/)**: Database Engineering, EXPLAIN ANALYZE, and Concurrency Analysis
- **[docs/v3/](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v3/)**: Container Topology & Redis Latency Laboratory
