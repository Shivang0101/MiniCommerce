# 🛒 MiniCommerce — Enterprise Security, Distributed Resilience & DevOps Automation (V6)

Welcome to **MiniCommerce**, an evolving, production-grade backend engineering and system design laboratory. 

MiniCommerce serves as a benchmark laboratory for exploring **high-throughput backend patterns**, **database optimization**, **pessimistic concurrency control**, **in-memory distributed caching**, **asynchronous task offloading**, **sliding-window rate limiting**, **zero-trust dual-token rotation**, **distributed resilience patterns**, **automated CI/CD pipelines**, and **container delivery**.

---

## 🚀 Key System Features (Version 6 Current State)

- **🛠️ Automated Git Pre-Commit Quality Hooks**: `.pre-commit-config.yaml` executing `ruff`, `ruff-format`, `black`, and `detect-secrets` leak scanning before git commits.
- **⚙️ Centralized Tooling Configuration (`pyproject.toml`)**: Unified quality rules for Ruff, Mypy type-checking, Pytest, and Coverage report generation (`coverage.xml`).
- **🔄 GitHub Actions CI Pipeline (`ci.yml`)**: Automated Pull Request and `main`/`develop` branch quality gates executing Ruff linting, Mypy static type checking, Bandit AST security scanning, Trivy vulnerability checks, and Pytest with `postgres:15-alpine` and `redis:7-alpine` service containers.
- **📦 GitHub Actions CD Container Pipeline (`cd.yml`)**: Automated Docker BuildKit multi-stage container builds pushing `backend`, `worker`, and `frontend` images directly to GitHub Container Registry (`ghcr.io`).
- **🔐 Dual-Token Zero-Trust Security**: Short-lived Access Tokens (15 min) in `Authorization: Bearer` headers + Long-lived Refresh Tokens (7 days) in `HttpOnly`, `SameSite=Lax` cookies. Automatic token rotation via `POST /api/v1/auth/refresh`.
- **🚫 Redis Token Revocation List (`TokenBlacklistService`)**: Instant JWT revocation on logout (`POST /api/v1/auth/logout`) or token rotation. `deps.get_current_user` rejects revoked tokens with `401 Unauthorized`.
- **🛡️ Scoped Role-Based Access Control (RBAC)**: Fine-grained roles (`CUSTOMER`, `STORE_MANAGER`, `SRE_ADMIN`) mapped to explicit permission scope lists (`products:read`, `products:write`, `products:delete`, `orders:create`, `admin:telemetry`).
- **⚡ Thread-Safe Circuit Breaker State Machine**: Isolates downstream datastore failures (`CLOSED` ➔ `OPEN` ➔ `HALF-OPEN`) when error rates exceed 50% over a 10s sliding window.
- **📦 Transactional Outbox Pattern Engine**: Inserts `outbox` event records inside the **exact same atomic SQL transaction** (`db.commit()`) as order checkouts. ARQ worker polls outbox events to guarantee 100% reliable side-effect processing.
- **🛑 Graceful Shutdown Handling**: FastAPI lifespan context intercepts SIGTERM/SIGINT signals to drain database connection pools (`await engine.dispose()`) and close Redis pools cleanly before shutdown.
- **📊 Health Probe Separation**: Separates `/healthz/liveness` (process liveness check) and `/healthz/readiness` (PostgreSQL + Redis downstream ping check returning `503 Service Unavailable` on store outages).
- **⏩ Keyset (Cursor-Based) Pagination**: Constant `O(1)` query execution via `GET /api/v1/products/keyset` (`WHERE id > :last_seen_id AND is_deleted = FALSE ORDER BY id ASC LIMIT :limit`), bypassing deep `OFFSET` buffer scan overheads.
- **🗑️ Soft Deletion & Audit Tracking**: Soft deletion via `DELETE /api/v1/products/{id}` (`is_deleted = True`, `deleted_at = now()`) protecting catalog historical integrity.
- **🔒 SHA-256 Payload-Hashed Idempotency Engine**: SHA-256 hash comparison on idempotency key reuse, returning `HTTP 409 Conflict` on request payload mismatches.
- **🏬 React Store Manager Portal & 401 Interceptor**: Store Manager Dashboard UI (`StoreManagerDashboard.jsx`) for product creation, stock restocking, and soft-deletion, supported by an Axios/Fetch 401 automatic token refresh interceptor in `api.js`.
- **📊 Datadog-Grade Enterprise Observability Dashboard**: Control panel featuring a System Operational Status Bar, top KPI metrics, live ARQ worker task log streams, and an OpenTelemetry-Style Distributed Waterfall Trace Visualizer.
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

#### 2. Pagination Deep `OFFSET` Overhead Bounds vs. V5 Keyset Pagination
| OFFSET / Cursor Value | Execution Latency | Query Plan Type | Buffer Hits | Takeaway |
|---|---|---|---|---|
| `OFFSET 0` | **0.08 ms** | Index Scan | 4 shared hit | Instant lookup |
| `OFFSET 100` | **0.22 ms** | Index Scan | 12 shared hit | Slight buffer read |
| `OFFSET 1,000` | **1.85 ms** | Index Scan (Skip scan) | 98 shared hit | Higher IO cost |
| `OFFSET 10,000` | **14.92 ms** | Bitmap Heap Scan | 742 shared hit | Degrades linearly as OFFSET increases |
| **V5 Keyset Cursor (`id > :last_seen_id`)** | **0.08 ms** | Index Seek | 4 shared hit | Constant O(1) performance regardless of depth |

---

### ⚡ Milestone 2: Impact of In-Memory Redis Caching (`docs/v3/performance.md`)

When retrieving the catalog (`GET /api/v1/products`) across 50,000 products:

| Query Strategy | Target Storage Tier | Avg Latency | p50 Latency | p95 Latency | Speedup Metric |
|---|---|---|---|---|---|
| **Direct Supabase Database Scan (V2)** | Remote AWS Cloud PostgreSQL | **102.4 ms** | 94.2 ms | 158.0 ms | Baseline (1x) |
| **Redis Cache-Aside Hit (V3)** | Local In-Memory Container | **2.8 ms** | 2.1 ms | 4.9 ms | **~36x Latency Reduction** |

---

### ⚡ Milestone 3: Impact of Asynchronous ARQ & Transactional Outbox Offloading (`docs/v4/benchmarks.md`, `docs/v5/resilience-and-outbox.md`)

When executing an atomic checkout transaction (`POST /api/v1/orders`):

| Checkout Execution Strategy | Target Queue / Processing Tier | Avg Latency | p50 Latency | p95 Latency | Speedup Metric |
|---|---|---|---|---|---|
| **Synchronous Model** (DB + Blocking Email + Audit) | Direct HTTP Request Execution | **139.2 ms** | 135.0 ms | 148.5 ms | Baseline (1.0x) |
| **V5 Async Outbox & ARQ Offloading** (DB Commit + Outbox Insert) | Post-Commit Redis ARQ Worker Pool | **14.2 ms** | 12.8 ms | 16.5 ms | **9.8x Response Speedup** |

---

## 🏗️ 5-Tier Data Layer Architecture

MiniCommerce strictly enforces a 5-tier separation of concerns across both local and containerized deployments:

```text
                                HTTP REQUEST
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 1. MIDDLEWARE PIPELINE                                                            |
|    LoggingMiddleware (Structured JSON Logs) ➔ RateLimiterMiddleware (Redis ZSET)  |
|    ➔ TokenBlacklistMiddleware (Redis Revocation) ➔ CORSMiddleware                |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 2. ROUTER LAYER (app/api/v1/)                                                     |
|    Thin HTTP controllers validating Pydantic schemas & RBAC Scopes               |
|    - auth.py (/refresh, /logout, /login) - products.py (catalog, /keyset, soft-del)|
|    - cart.py (items management)         - orders.py (idempotent checkout & status)|
|    - admin.py (metrics, queue, traces)  - health.py (/healthz/liveness & readiness)|
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 3. SERVICE LAYER (app/services/)                                                  |
|    Business rules, domain invariants, transaction control, cache-aside & outbox       |
|    - AuthService (password verification, dual JWT issuance & scope mappings)      |
|    - ProductService (cache hit/miss handling & soft-delete cache purging)         |
|    - OrderService (payload-hashed idempotency, FOR UPDATE locks, Outbox events)   |
|    - TokenBlacklistService & TraceService (Redis revocation list & traces)        |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 4. REPOSITORY LAYER (app/repositories/)                                           |
|    Encapsulated Data Access isolating SQLAlchemy query execution                  |
|    - UserRepository (email, UUID lookups & role scope resolution)                 |
|    - ProductRepository (OFFSET & Keyset pagination, FOR UPDATE locks, soft delete)|
|    - CartRepository (eager relationship loading)                                  |
|    - OrderRepository & OutboxRepository (order persistence & outbox event CRUD)   |
+-----------------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------------+
| 5. PERSISTENCE, QUEUE & WORKER TIER                                               |
|    - Redis 7 Container (Cache Pool, Revocation Blacklist & ARQ Queue on Port 6379)   |
|    - ARQ Background Worker Container (minicommerce-worker: outbox processor)      |
|    - Supabase PostgreSQL DB (Users, Products, Orders, Outbox on AWS Cloud)         |
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
│  └─ Large Dataset Benchmarking (409,913 Records on Supabase AWS Cloud)            │
│                                                                                   │
│  [VERSION 3] Containerization, Distributed Caching & Resilient State              │
│  ├─ Multi-Container Topology (FastAPI Backend, Redis 7 Alpine, Nginx SPA)          │
│  ├─ Async Redis Cache-Aside Pattern (~36x Catalog Latency Speedup: 102ms ➔ 2.8ms) │
│  ├─ Write Invalidation Engine (Automatic Cache Purging on Order Checkout)        │
│  └─ Resilient DB Fallback (0.2s Failover: 0% HTTP 500 error impact when Redis down)│
│                                                                                   │
│  [VERSION 4] Async Task Queue, Rate Limiting & Admin Observability                │
│  ├─ ARQ Redis Worker Pool (Decoupled Receipt Email, Stock Audit & Analytics)     │
│  ├─ Sliding-Window Rate Limiter Middleware (Redis ZSETs with Tier Thresholds)    │
│  └─ Secured Admin Observability Dashboard (/admin UI + JWT is_admin Protection)   │
│                                                                                   │
│  [VERSION 5] Enterprise Security, Distributed Resilience & Data Engineering       │
│  ├─ Dual-Token Rotation (Access JWT + HttpOnly Refresh Cookie + /auth/refresh)   │
│  ├─ Redis Token Revocation List (Logout blacklist matching token TTL)            │
│  ├─ Scoped Role-Based Access Control (CUSTOMER, STORE_MANAGER, SRE_ADMIN)         │
│  ├─ Thread-Safe Circuit Breaker State Machine (CLOSED -> OPEN -> HALF-OPEN)      │
│  ├─ Transactional Outbox Pattern Engine (Atomic SQL transaction outbox events)    │
│  ├─ Health Probe Separation (/healthz/liveness & /healthz/readiness)             │
│  ├─ Keyset Cursor Pagination (O(1) execution avoiding deep OFFSET scans)         │
│  ├─ Soft Delete Architecture & SHA-256 Payload-Hashed Idempotency Engine          │
│  └─ Store Manager Portal UI & Axios 401 Automatic Token Refresh Interceptor      │
│                                                                                   │
│  [VERSION 6] DevOps Automation & CI/CD Pipeline Engineering (Current)             │
│  ├─ Git Pre-Commit Hooks (Ruff, Black, Detect-Secrets, YAML/JSON formatters)      │
│  ├─ Centralized Tool Configuration (pyproject.toml: Ruff, Mypy, Pytest, Cov >= 85%)│
│  ├─ GitHub Actions CI Pipeline (Linting, Mypy, Bandit, Trivy, Pytest Services)    │
│  └─ GitHub Actions CD Pipeline (Multi-Stage Docker builds & GHCR delivery)        │
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
- **Store Manager Portal**: Access via Navbar (Login as `STORE_MANAGER` or `SRE_ADMIN`)
- **Admin Observability Panel**: [http://localhost:3000](http://localhost:3000) (Click `Admin Panel` in Navbar; Default Credentials: `admin@minicommerce.com` / `Admin@123456`)
- **FastAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Liveness Probe (`/healthz/liveness`)**: [http://localhost:8000/healthz/liveness](http://localhost:8000/healthz/liveness)
- **Readiness Probe (`/healthz/readiness`)**: [http://localhost:8000/healthz/readiness](http://localhost:8000/healthz/readiness)

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

# 1. Run full 40-test integration, security, resilience, outbox & data engineering suite
python -m pytest -v

# 2. Re-run performance laboratory benchmarks
python app/db/run_benchmarks.py
```

---

## 📝 Technical Documentation Suite
Detailed architectural specifications and experiment logs:
- **[v/v1.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v1.txt)**: Version 1 Master Specification
- **[v/v2.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v2.txt)**: Version 2 Master Specification
- **[v/v3.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v3.txt)**: Version 3 Master Specification
- **[v/v4.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v4.txt)**: Version 4 Master Specification & Work Log
- **[v/v5.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v5.txt)**: Version 5 Master Specification & Work Log
- **[v/v6.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v6.txt)**: Version 6 Master Specification & Work Log
- **[docs/v5/security-and-rbac.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v5/security-and-rbac.md)**: Zero-Trust Security, Token Rotation & Scoped RBAC
- **[docs/v5/resilience-and-outbox.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v5/resilience-and-outbox.md)**: Circuit Breakers, Transactional Outbox & Signal Handling
- **[docs/v5/data-engineering.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v5/data-engineering.md)**: Keyset Pagination, Soft Deletes & Payload Hashing
- **[docs/v5/frontend-architecture.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v5/frontend-architecture.md)**: Store Manager Portal & 401 Interceptor Architecture
- **[docs/v5/troubleshooting.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v5/troubleshooting.md)**: Comprehensive V5 Error Log & Resolution Tracker
- **[docs/v6/devops-and-cicd.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v6/devops-and-cicd.md)**: DevOps Automation, Pre-Commit Hooks & CI/CD Pipeline Architecture
