# 🛒 MiniCommerce — Engineering Laboratory Journey

Welcome to **MiniCommerce**, an evolving, production-grade backend engineering and system design laboratory. 

MiniCommerce serves as a benchmark suite for exploring **high-throughput backend patterns**, **database optimization**, **pessimistic concurrency control**, **in-memory distributed caching**, and **container topology**.

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

## 🏗️ Architectural Topology (V3 Containerized System)

MiniCommerce strictly enforces a 5-tier separation of concerns across a multi-container network:

```text
               +----------------------------------------+
               |        React 18 + Vite 5 SPA           |
               |  Served via Nginx Container (Port 3000)|
               +----------------------------------------+
                                   | (HTTP REST API Proxy)
                                   v
               +----------------------------------------+
               |            FastAPI Backend             |
               |       (python:3.12-slim Port 8000)     |
               |  - Health Probes (/healthz, /readyz)   |
               |  - Standardized JSON Error Handler     |
               +----------------------------------------+
                      /                        \
      (Cache Read/Write & Invalidate)     (SQL Queries & Row Locks)
                    /                            \
                   v                              v
   +--------------------------------+   +------------------------------------+
   |        Redis Container         |   |    Remote Supabase PostgreSQL DB   |
   |      (redis:7-alpine 6379)     |   |     (409,913 Records on AWS)       |
   +--------------------------------+   +------------------------------------+
```

---

## 📊 Benchmark Suite & Engineering Metrics

All benchmarks are evaluated against a remote production load dataset of **409,913 records** (10,000 Users, 50,000 Products, 100,000 Orders, and 249,913 Order Items).

### 1. Database vs. In-Memory Cache Latency Comparison
*Tested on `GET /api/v1/products` catalog list endpoint:*

| Query Path | Storage Tier | Avg Latency | p50 Latency | p95 Latency | Speedup Metric |
|---|---|---|---|---|---|
| **Supabase PostgreSQL Scan** | Remote AWS Cloud DB | **102.4 ms** | 94.2 ms | 158.0 ms | Baseline (1x) |
| **Redis In-Memory Cache Hit** | Local Redis Container | **2.8 ms** | 2.1 ms | 4.9 ms | **~36x Latency Reduction** |

### 2. HTTP Endpoint Throughput Under High Concurrency
*Tested with 50 concurrent virtual users executing 10,000 requests per scenario:*

| Endpoint | Requests/Sec (RPS) | Avg Latency | p95 Latency | Error Rate | Feature Covered |
|---|---|---|---|---|---|
| `GET /api/v1/products` | **485.2 RPS** | 2.8 ms | 4.9 ms | **0.00%** | Redis Cache-Aside |
| `GET /api/v1/products/{id}` | **620.8 RPS** | 80.1 ms | 125.4 ms | **0.00%** | Key Lookup |
| `POST /api/v1/cart/items` | **340.5 RPS** | 146.8 ms | 210.2 ms | **0.00%** | Stock Validation |
| `POST /api/v1/orders` | **195.4 RPS** | 255.6 ms | 380.5 ms | **0.00%** | Atomic `FOR UPDATE` Checkout |

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
