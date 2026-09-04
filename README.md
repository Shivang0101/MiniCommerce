# 🛒 MiniCommerce — Enterprise AWS Cloud Architecture, Observability, Read Replicas & Chaos Engineering (V9)

Welcome to **MiniCommerce**, an evolving, production-grade backend engineering, cloud architecture, and system design laboratory. 

MiniCommerce serves as a benchmark laboratory for exploring **Infrastructure as Code (Terraform)**, **AWS Cloud Architecture (VPC, ECS Fargate, RDS PostgreSQL Multi-AZ, ElastiCache Redis, ALB, WAF)**, **Amazon Managed Prometheus (AMP) & Amazon Managed Grafana (AMG)**, **Prometheus Telemetry & Grafana SRE Dashboards**, **OpenTelemetry Distributed Tracing**, **Database Read-Replica Connection Splitting**, **Locust Concurrency & Chaos Stress Testing**, **high-throughput backend patterns**, **database optimization**, **pessimistic concurrency control**, **in-memory distributed caching**, **asynchronous task offloading**, **sliding-window rate limiting**, **zero-trust dual-token rotation**, **distributed resilience patterns**, **automated CI/CD pipelines**, and **cloud container delivery**.

---

## 🚀 Key System Features (Version 9 Current State)

- **🔀 Database Read-Replica Connection Splitting (`get_read_db`)**: Dual SQLAlchemy async engines (`primary_engine` for mutations and `replica_engine` for read queries) offloading catalog browsing and revenue analytics queries to read replicas with automatic primary fallback.
- **🧪 Locust High-Concurrency Load & Resilience Stress Suite (`locustfile.py` & `run_chaos_test.py`)**: Scriptable load generator simulating 1,000+ unique authenticated virtual users (with distinct UUIDs and JWT tokens) executing catalog search, cart operations, and idempotent checkouts.
- **🛡️ AWS WAF (Web Application Firewall) & Security Hardening Module**: Terraform HCL module (`terraform/modules/waf/`) attaching a regional Web ACL to the Application Load Balancer with SQLi, XSS, payload inspection, and 1,000 req/5m IP rate limiting.
- **🌋 Disaster Recovery & Chaos Engineering Runbook (`docs/v9/chaos-and-dr.md`)**: Complete SRE operational runbook documenting RTO < 30s, RPO = 0s (guaranteed by Transactional Outbox pattern), and failure injection procedures.

- **📊 Prometheus Telemetry Engine & Exporter (`/metrics`)**: Exposes standard Prometheus metrics format on `GET /metrics` via `prometheus-fastapi-instrumentator` with custom SRE metrics (`http_requests_total`, `http_request_duration_seconds`, `db_pool_connections_active`, `redis_cache_hits_total`, `redis_cache_misses_total`, `circuit_breaker_state`, `outbox_events_pending_total`, `outbox_events_dlq_total`).
- **📈 Pre-Built Grafana SRE Dashboards**: Auto-provisioned Grafana dashboards (`golden_signals.json` for p50/p95/p99 Latency, RPS by route, Error % gauge, Saturation; `database_and_cache.json` for DB connection pool utilization, Redis hit rate %, Circuit Breakers timeline, Outbox DLQ).
- **🚨 SRE Alertmanager Rules (`alerts.yml`)**: Automated alert rules (`HighFiveHundredErrorRate`, `CircuitBreakerOpen`, `OutboxDLQBacklog`, `HighLatencyP95`) evaluating operational thresholds every 15 seconds.
- **🔍 OpenTelemetry & Jaeger Distributed Tracing**: OTLP trace span exporter tracking distributed request propagation across Nginx ➔ FastAPI ➔ PostgreSQL ➔ Redis ➔ ARQ Worker.
- **☁️ Amazon Managed Prometheus (AMP) & Grafana (AMG) via Terraform**: Reusable HCL module in `terraform/modules/observability/` provisioning `aws_prometheus_workspace`, `aws_grafana_workspace`, and IAM `aps:RemoteWrite` task execution policies.
- **🧪 46-Test Automated Pytest Telemetry Suite**: 100% passing test coverage including `backend/tests/test_telemetry.py` asserting `/metrics` HTTP 200 exposition, counter increments, and circuit breaker state tracking.
- **🏗️ Infrastructure as Code (IaC) via Terraform**: 7 production-grade reusable HCL modules in `terraform/modules/` (`vpc`, `rds`, `elasticache`, `alb`, `ecs`, `iam_and_secrets`, `observability`) provisioning AWS cloud resources with zero manual click-ops.
- **🌐 Dual-AZ VPC Network Topology**: Multi-AZ VPC across `us-east-1a` and `us-east-1b` with Public Subnets (ALB, Fargate Tasks), Private App Subnets, and Private Database Subnets (RDS, ElastiCache Redis).
- **⚖️ AWS Application Load Balancer (ALB)**: High-availability internet-facing ALB routing traffic dynamically via path rules (`/api/*` ➔ Backend Target Group port 8000, `/*` ➔ Frontend Target Group port 80).
- **🚢 AWS ECS Fargate Container Orchestration**: Serverless container execution for `backend` (FastAPI), `worker` (ARQ Background Task Processor), and `frontend` (Nginx React SPA) with auto-scaling security groups and CloudWatch logging streams.
- **🐘 AWS RDS PostgreSQL 15 Engine**: Multi-AZ capable database tier running in isolated Private DB subnets with automated daily backups and KMS storage encryption.
- **⚡ AWS ElastiCache Redis Replication Cluster**: High-speed in-memory cache and ARQ task queue cluster running in Private DB subnets with At-Rest & Transit (TLS) Encryption.
- **🔐 AWS Secrets Manager Integration**: Dynamic retrieval of database credentials, Redis AUTH tokens, and JWT signing keys via boto3 runtime fetching (`app/core/cloud_secrets.py`).
- **🌱 Automated 1-Shot Database Seeding**: Automated Fargate 1-shot task execution (`python app/db/seed.py`) seeding admin accounts, users, hardware catalog, and simulated orders directly into live AWS RDS PostgreSQL.
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
- **🐳 Multi-Container Orchestration**: Production-ready `docker-compose.yml` orchestrating `backend` (FastAPI), `redis` (Redis 7 Alpine), `worker` (ARQ Background Worker), `frontend` (Nginx Alpine), `prometheus` (Port 9090), `grafana` (Port 3001), and `jaeger` (Port 16686).

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
|    - ProductService (cache hit/miss metrics & soft-delete cache purging)         |
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
| 5. PERSISTENCE, QUEUE & OBSERVABILITY TIER                                        |
|    - Redis 7 Container (Cache Pool, Revocation Blacklist & ARQ Queue on Port 6379)   |
|    - ARQ Background Worker Container (minicommerce-worker: outbox processor)      |
|    - Prometheus Container (Port 9090: Scrapes /metrics endpoint & evaluates alerts)  |
|    - Grafana Container (Port 3001: Golden Signals & DB/Cache SRE Dashboards)      |
|    - Jaeger Container (Port 16686: OpenTelemetry Distributed Trace Collector)     |
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
│  [VERSION 6] DevOps Automation & CI/CD Pipeline Engineering                        │
│  ├─ Git Pre-Commit Hooks (Ruff, Black, Detect-Secrets, YAML/JSON formatters)      │
│  ├─ Centralized Tool Configuration (pyproject.toml: Ruff, Mypy, Pytest, Cov >= 85%)│
│  ├─ GitHub Actions CI Pipeline (Linting, Mypy, Bandit, Trivy, Pytest Services)    │
│  └─ GitHub Actions CD Pipeline (Multi-Stage Docker builds & GHCR delivery)        │
│                                                                                   │
│  [VERSION 7] Infrastructure as Code (IaC) & AWS Cloud Architecture                │
│  ├─ Terraform Modular HCL (6 Packages: VPC, RDS, ElastiCache, ALB, ECS, Secrets)  │
│  ├─ Dual-AZ VPC Network (Public Subnets, Private App Subnets, Private DB Subnets) │
│  ├─ AWS ECS Fargate Orchestration (backend, worker, frontend multi-container)     │
│  ├─ AWS RDS PostgreSQL 15 & ElastiCache Redis Cluster (TLS Transit Encryption)    │
│  ├─ AWS Secrets Manager (Dynamic Boto3 secret fetcher in app/core/cloud_secrets.py)│
│  └─ Automated 1-Shot Fargate Seeding (Seeded Admin, Users, Products to RDS)       │
│                                                                                   │
│  [VERSION 8] Enterprise Observability & Site Reliability Engineering              │
│  ├─ Prometheus Telemetry Engine (/metrics endpoint with custom counters & gauges) │
│  ├─ Pre-Built Grafana Dashboards (The 4 Golden Signals & DB/Cache SRE Dashboards) │
│  ├─ SRE Alertmanager Rules (High 5xx, CircuitBreakerOpen, DLQ Backlog, p95 Spike) │
│  ├─ OpenTelemetry & Jaeger Distributed Tracing (OTLP request span propagation)    │
│  ├─ Amazon Managed Prometheus (AMP) & Amazon Managed Grafana (AMG) in Terraform   │
│  └─ Automated Pytest Telemetry Suite (100% Pass Rate: 46/46 Backend Test Suite)  │
│                                                                                   │
│  [VERSION 9] Cloud-Native High Availability, Disaster Recovery & Chaos (Current)  │
│  ├─ Database Read-Replica Connection Splitting (primary_engine & replica_engine)  │
│  ├─ Locust High-Concurrency Load Suite (1,000+ unique virtual user journey simulation)│
│  ├─ AWS WAF (Web Application Firewall) IaC Module (Rate limits, SQLi & XSS protection)│
│  └─ Disaster Recovery & Chaos Engineering Runbook (docs/v9/chaos-and-dr.md: RTO < 30s)│
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Execution Guide: Docker & Local Replication (Version 9)

Follow these exact step-by-step commands to replicate, benchmark, and test all **Version 9** features locally using **Docker Compose**:

### 1. Launch Container Stack via Docker Compose
Launch the full containerized topology (FastAPI Backend, Redis 7, ARQ Worker, React Frontend, Prometheus, Grafana, Jaeger):
```powershell
docker compose up --build
```
- **React Storefront SPA**: [http://localhost:3000](http://localhost:3000)
- **Store Manager Portal**: Access via Navbar (Login as `STORE_MANAGER` or `SRE_ADMIN`)
- **Admin Observability Panel**: [http://localhost:3000](http://localhost:3000) (Click `Admin Panel` in Navbar; Credentials: `admin@minicommerce.com` / `Admin@123456`)
- **Prometheus Metrics Exporter**: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- **Prometheus Web UI**: [http://localhost:9090](http://localhost:9090)
- **Grafana SRE Dashboards**: [http://localhost:3001](http://localhost:3001) (Credentials: `admin` / `admin`)
- **Jaeger Distributed Tracing UI**: [http://localhost:16686](http://localhost:16686)
- **FastAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Liveness Probe (`/healthz/liveness`)**: [http://localhost:8000/healthz/liveness](http://localhost:8000/healthz/liveness)
- **Readiness Probe (`/healthz/readiness`)**: [http://localhost:8000/healthz/readiness](http://localhost:8000/healthz/readiness)

---

### 2. Verify API Read Replica Connection Splitting
Test the catalog keyset endpoint routed via `get_read_db()`:
```powershell
curl http://localhost:8000/api/v1/products/keyset?limit=10
```
- **Expected Result**: Returns `HTTP 200 OK` with JSON catalog array. When `READ_DATABASE_URL` is omitted locally, `get_read_db()` gracefully falls back to your primary database.

---

### 3. Run Automated 49-Test Pytest Suite
Run the full unit, integration, telemetry, security, and read-replica test suite:
```powershell
backend\.venv\Scripts\python.exe -m pytest -v
```
- **Expected Result**: `49 passed in ~28s` (100% pass rate).

---

### 4. Run Chaos Engineering Resilience Stress Script
Run the automated failure injection and resilience test:
```powershell
backend\.venv\Scripts\python.exe backend/tests/load/run_chaos_test.py
```
- **Expected Result**: `[PASSED] CHAOS EXPERIMENT COMPLETE! 0% HTTP 500 Failures under load.` across 150 concurrent workflows.

---

### 5. Run Locust High-Concurrency Load Testing Suite

#### Option A: Headless CLI Mode (Automated 30s Run)
Simulate 50 concurrent virtual users generating request volume against your local Docker backend:
```powershell
backend\.venv\Scripts\python.exe -m locust -f backend/tests/load/locustfile.py --headless -u 50 -r 10 --run-time 30s --host http://localhost:8000
```
- **Expected Result**: Executes ~1,000 requests in 30s. Catalog read endpoints (`/products` & `/products/keyset`) maintain **0% error rate** with sub-150ms median response times.

#### Option B: Interactive Web UI Mode
Launch Locust with an interactive web dashboard:
```powershell
backend\.venv\Scripts\python.exe -m locust -f backend/tests/load/locustfile.py --host http://localhost:8000
```
1. Open [http://localhost:8089](http://localhost:8089) in your browser.
2. Set **Number of users**: `50`, **Ramp-up rate**: `10`.
3. Click **Start Swarming** to watch live RPS charts, response percentiles (p50/p95), and user concurrency metrics!

---

### 6. Run Code Quality & Static Type Verification
```powershell
# 1. Code Formatting & Linting
backend\.venv\Scripts\python.exe -m ruff check backend/app

# 2. Static Type Checking
backend\.venv\Scripts\mypy.exe backend/app
```

---

### Option B: Run Locally Without Docker (Separately)

#### 1. Launch Backend Server (Terminal 1)
```powershell
cd backend
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

### Option C: Run Automated Test & Quality Check Suites

```powershell
cd backend
.\.venv\Scripts\Activate.ps1

# 1. Run full 46-test telemetry, security, resilience, outbox & data engineering suite
python -m pytest -v

# 2. Run telemetry-specific test suite
python -m pytest backend/tests/test_telemetry.py -v

# 3. Run static code linting & mypy type checking
ruff check backend/app
mypy backend/app

# 4. Re-run performance laboratory benchmarks
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
- **[v/v7.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v7.txt)**: Version 7 Master Specification & Work Log
- **[v/v8.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v8.txt)**: Version 8 Master Specification & Work Log
- **[v/v9.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v9.txt)**: Version 9 Master Specification & Work Log
- **[docs/v9/chaos-and-dr.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v9/chaos-and-dr.md)**: Cloud-Native High Availability, Disaster Recovery & Chaos Engineering Runbook
- **[docs/v8/observability-and-sre.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v8/observability-and-sre.md)**: Observability Engine, Prometheus, Grafana & SRE Runbook
- **[docs/v7/aws-cloud-architecture.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v7/aws-cloud-architecture.md)**: Infrastructure as Code & AWS Cloud Architecture Specification
- **[docs/v7/v7_postmortem_and_troubleshooting.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v7/v7_postmortem_and_troubleshooting.md)**: AWS Deployment Post-Mortem, Log Evidence & Troubleshooting Guide
- **[docs/v7/terraform_run.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v7/terraform_run.txt)**: Live Terraform Execution & Provisioning Outputs
- **[docs/v5/security-and-rbac.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v5/security-and-rbac.md)**: Zero-Trust Security, Token Rotation & Scoped RBAC
- **[docs/v5/resilience-and-outbox.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v5/resilience-and-outbox.md)**: Circuit Breakers, Transactional Outbox & Signal Handling
- **[docs/v5/data-engineering.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v5/data-engineering.md)**: Keyset Pagination, Soft Deletes & Payload Hashing
- **[docs/v5/frontend-architecture.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v5/frontend-architecture.md)**: Store Manager Portal & 401 Interceptor Architecture
- **[docs/v5/troubleshooting.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v5/troubleshooting.md)**: Comprehensive V5 Error Log & Resolution Tracker
- **[docs/v6/devops-and-cicd.md](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v6/devops-and-cicd.md)**: DevOps Automation, Pre-Commit Hooks & CI/CD Pipeline Architecture
