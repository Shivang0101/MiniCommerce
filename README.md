# MiniCommerce V3 — Containerization, In-Memory Caching & Distributed State Resilience

**MiniCommerce V3** is an advanced backend engineering laboratory built with **FastAPI**, **PostgreSQL** (via Supabase Cloud), **Redis 7** (In-Memory Cache), **Docker Compose**, **SQLAlchemy 2.x ORM**, **Alembic**, **JWT Authentication**, and **Atomic Transactions**, complemented by a modern React 18 + Vite 5 Single Page Application (SPA).

Version 3 shifts focus to **Local Multi-Container Orchestration, Async Redis Cache-Aside Pattern, Write Cache Invalidation, Resilient DB Fallback, Distributed Health Probes (`/healthz`, `/readyz`), and Container Performance Benchmarking**.

---

## 🏗️ Architectural Overview (Containerized Topology & Data Layer)

MiniCommerce V3 enforces an orchestrated container topology with a 5-tier backend separation of concerns:

```text
React 18 + Vite 5 SPA (Served via Nginx Container on Port 3000)
     │
     ▼ (HTTP REST API Reverse Proxy)
FastAPI Backend (python:3.12-slim Container on Port 8000)
     ├── Health & Readiness Probes (/healthz, /readyz)
     ├── Middleware Pipeline (RequestIdMiddleware, LoggingMiddleware, CORSMiddleware)
     ├── Router Layer (Thin route handlers: app/api/v1/)
     ├── Service Layer (Business rules, Transaction boundaries, Cache-Aside logic)
     ├── Repository Layer (Encapsulated Data Access: app/repositories/)
     └── Data Persistence & State Resilience:
          ├── Redis In-Memory Cache (redis:7-alpine Container on Port 6379)
          └── PostgreSQL DB (409,913 Records on Remote Supabase AWS Cloud)
```

### Architectural Principles & V3 Additions
1. **Container Orchestration (`docker-compose.yml`)**: Single-command startup (`docker compose up --build`) launching `backend`, `redis`, and `frontend` services with automated container health dependency checks.
2. **Async Redis Caching (`Cache-Aside`)**: Product catalog reads (`GET /api/v1/products`) are cached in Redis with a 300-second TTL, reducing latency by **~36x** (from 102ms down to 2.8ms).
3. **Write Invalidation**: Order checkouts (`POST /api/v1/orders`) and new product creation purge matching Redis cache keys (`products:*`) to prevent stale inventory reads.
4. **Fault Tolerance & Graceful Fallback**: If Redis becomes unreachable, down, or times out, the backend logs a warning and seamlessly falls back to direct Supabase PostgreSQL queries with 0% client HTTP 500 errors.
5. **Health & Readiness Probes**: `/healthz` checks FastAPI liveness; `/readyz` actively verifies downstream connections to both Supabase PostgreSQL and Redis.
6. **Zero Local DB Overhead**: Container topology directly connects to the remote 409k-record Supabase PostgreSQL instance, preserving local disk space.

---

## 📁 Project Directory Structure

```text
MiniCommerce/
├── README.md                 # Master Project Overview & Guide
├── next_implementation_plan  # Version Specification & Work Tracker
├── docker-compose.yml        # V3 Multi-Container Orchestration Manifest
├── .env.example              # Environment Configuration Template
├── .gitignore                # Git Ignore Rules
│
├── docs/                     # Technical Documentation Laboratory
│   ├── v2/                   # Version 2 Engineering Modules
│   └── v3/                   # Version 3 Container & Caching Modules
│       ├── architecture.md   # Container Topology & Cache Flow Diagram
│       └── performance.md    # Redis Cache Hit vs. DB Direct Latency Benchmarks
│
├── v/                        # Master Version Documentation
│   ├── v1.txt                # Version 1 Master Specification & Work Log
│   ├── v2.txt                # Version 2 Master Specification & Work Log
│   ├── v3.txt                # Version 3 Master Specification & Work Log
│   └── script.txt            # Master Roadmap & Specification Guide
│
├── backend/                  # FastAPI Application Root
│   ├── Dockerfile            # Python 3.12-slim Container Definition
│   ├── app/
│   │   ├── api/v1/           # Thin Route Handlers & Health Probes
│   │   ├── core/             # Settings, Security, Standardized Errors & Redis Pool
│   │   ├── middleware/       # Request ID & Latency Logging
│   │   ├── models/           # SQLAlchemy 2.x ORM Models
│   │   ├── schemas/          # Pydantic API Schemas
│   │   ├── repositories/     # Encapsulated Data Access Layer
│   │   ├── services/         # Business Logic, Cache-Aside & Transactions
│   │   │   ├── cache_service.py # Redis Cache GET/SET/Invalidate Logic
│   │   └── main.py           # FastAPI Entrypoint & Lifespan Handler
│   ├── tests/                # Pytest Integration, Concurrency & Cache Suite
│   └── requirements.txt
│
└── frontend/                 # React 18 + Vite 5 SPA Client
    ├── Dockerfile            # Multi-Stage Build (Node 20 -> Nginx alpine)
    ├── nginx.conf            # Nginx Reverse Proxy Config (/api -> backend:8000)
    ├── src/                  # React SPA Source Code & Lucide Icons
    └── package.json
```

---

## ⚡ Quick Start Guide (Containerized & Local)

### Option A: Run with Docker Compose (Recommended)
Make sure **Docker Desktop** is running, then run:
```powershell
docker compose up --build
```
- **Web App**: [http://localhost:3000](http://localhost:3000)
- **API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Liveness Probe**: [http://localhost:8000/healthz](http://localhost:8000/healthz)
- **Readiness Probe**: [http://localhost:8000/readyz](http://localhost:8000/readyz)

---

### Option B: Run Locally without Docker

#### 1. Setup Virtual Environment & Install Dependencies
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### 2. Configure Database & Environment
Copy `.env.example` to `.env` or `backend/.env` with your Supabase connection string.

#### 3. Run Pytest Suite
```powershell
python -m pytest -v
```
*Expected: 27/27 tests passing cleanly.*

#### 4. Run Benchmarks Laboratory
```powershell
python -m app.db.run_benchmarks
```

#### 5. Launch Backend Server
```powershell
uvicorn app.main:app --reload --port 8000
```

#### 6. Launch Frontend SPA
In a separate terminal:
```powershell
cd frontend
npm install
npm run dev
```

---

## 🔍 How to Inspect Redis Caching & Commands

Run these commands in a separate terminal while your containers are running:

```powershell
# 1. List all active cached product keys in Redis
docker exec -it minicommerce-redis redis-cli KEYS "products:*"

# 2. View raw JSON contents of a cached key
docker exec -it minicommerce-redis redis-cli GET "products:page=1:size=12:min=None:max=None:sb=name:so=asc:q=None:c=None"

# 3. View remaining TTL (Time-To-Live in seconds)
docker exec -it minicommerce-redis redis-cli TTL "products:page=1:size=12:min=None:max=None:sb=name:so=asc:q=None:c=None"

# 4. Stream live Redis commands as you navigate the web app
docker exec -it minicommerce-redis redis-cli MONITOR
```

---

## 📊 Performance & Cache Benchmarks

All benchmarks are evaluated against a remote Supabase production load dataset of **409,913 records**.

### Product Catalog Query (`GET /api/v1/products`) Latency Metrics

| Scenario | Data Target | Avg Latency (ms) | p50 Latency (ms) | p95 Latency (ms) | Latency Speedup |
|---|---|---|---|---|---|
| **Direct Supabase PostgreSQL Scan** | Remote AWS Cloud DB | **102.4 ms** | 94.2 ms | 158.0 ms | Baseline (1x) |
| **Redis Cache Hit** | Local Redis Container | **2.8 ms** | 2.1 ms | 4.9 ms | **~36x Speedup** |

---

## 📝 Technical Documentation Suite
Refer to **[v/v3.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/v/v3.txt)** and **[docs/v3/](file:///d:/shivang/Project/MLProjects/MiniCommerce/docs/v3/)** for full architectural blueprints, container error resolution logs, and caching verification steps.
