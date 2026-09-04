# 🧪 MiniCommerce V9 — Local Testing & Docker Replication Guide

This guide provides step-by-step instructions to replicate, benchmark, and test all **Version 9 (V9)** features locally using **Docker Compose**.

---

## 🚀 Prerequisites

1. **Docker Desktop**: Running locally (`docker compose up` active).
2. **Python Virtual Environment**: `.venv` initialized inside `backend/` (`backend\.venv`).

---

## 📋 Step-by-Step Local Execution Commands

### Step 1: Launch Local Container Topology
Launch the full containerized environment (FastAPI Backend, Redis 7, ARQ Worker, React Frontend, Prometheus, Grafana, Jaeger):

```powershell
docker compose up --build
```

**Local Ports & Dashboard URLs**:
- **FastAPI Backend API**: [http://localhost:8000](http://localhost:8000)
- **FastAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **React Frontend Storefront**: [http://localhost:3000](http://localhost:3000)
- **Grafana SRE Dashboards**: [http://localhost:3001](http://localhost:3001) *(Login: `admin` / `admin`)*
- **Prometheus Metrics Web UI**: [http://localhost:9090](http://localhost:9090)
- **Jaeger Distributed Tracing UI**: [http://localhost:16686](http://localhost:16686)

---

### Step 2: Verify API Read-Replica Connection Splitting
Test the catalog keyset endpoint routed via `get_read_db()`:

**PowerShell**:
```powershell
curl http://localhost:8000/api/v1/products/keyset?limit=10
```

**Bash / Linux**:
```bash
curl -s http://localhost:8000/api/v1/products/keyset?limit=10 | jq .
```
- **Expected Output**: Returns `HTTP 200 OK` with JSON catalog array. When `READ_DATABASE_URL` is omitted locally, `get_read_db()` gracefully falls back to your primary database with 0 error impact.

---

### Step 3: Run Full Pytest Automated Suite (49 Tests)
Run the automated unit, integration, security, and read-replica test suite:

```powershell
backend\.venv\Scripts\python.exe -m pytest -v
```
- **Expected Output**: `49 passed in ~28s` (100% pass rate).

---

### Step 4: Run Chaos Engineering Stress Script
Run the automated failure injection and resilience test:

```powershell
backend\.venv\Scripts\python.exe backend/tests/load/run_chaos_test.py
```
- **Expected Output**:
  ```text
  ================================================================================
                        CHAOS TEST EXPERIMENT RESULTS                     
  ================================================================================
  Total Workflows Executed: 150
  Successful Workflows:    150
  Failed Workflows (500s): 0
  Total Execution Time:    ~14 seconds
  Average Throughput:      ~10.7 RPS
  p50 Median Latency:      ~800 ms
  Status Code Summary:     {200: 150}
  ================================================================================
  [PASSED] CHAOS EXPERIMENT COMPLETE! 0% HTTP 500 Failures under load.
  ```

---

### Step 5: Run Locust High-Concurrency Load Testing Suite

#### Option A: Headless Automated CLI Run (30 Seconds)
Simulate 50 concurrent virtual users generating high request throughput against your local Docker backend:

```powershell
backend\.venv\Scripts\python.exe -m locust -f backend/tests/load/locustfile.py --headless -u 50 -r 10 --run-time 30s --host http://localhost:8000
```
- **Expected Output**: Executes ~1,000 requests in 30s. Catalog read endpoints (`/products` & `/products/keyset`) maintain **0% error rate** with sub-150ms median response times.

#### Option B: Interactive Web UI Mode
Launch Locust with an interactive web control panel:

```powershell
backend\.venv\Scripts\python.exe -m locust -f backend/tests/load/locustfile.py --host http://localhost:8000
```
1. Open [http://localhost:8089](http://localhost:8089) in your browser.
2. Set **Number of users**: `50`.
3. Set **Ramp-up rate**: `10`.
4. Click **Start Swarming**.
5. Watch live RPS graphs, response time percentiles (p50/p95/p99), and active virtual user counts!

---

### Step 6: Code Quality & Static Type Verification
Run static linter and type-checker commands:

```powershell
# 1. Static Code Formatting & Linting
backend\.venv\Scripts\python.exe -m ruff check backend/app

# 2. Static Type Verification
backend\.venv\Scripts\mypy.exe backend/app
```
- **Expected Output**: `All checks passed!` and `Success: no issues found in 46 source files`.
