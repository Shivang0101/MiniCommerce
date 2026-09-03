# MiniCommerce V8 - Enterprise Observability & Site Reliability Engineering (SRE) Runbook

## Overview

Version 8 introduces full-stack observability for MiniCommerce across both local development (Docker Compose) and production AWS Cloud Infrastructure (Amazon Managed Prometheus & Amazon Managed Grafana).

---

## 1. System Architecture & Data Flow

```
[FastAPI App] ──(/metrics)──► [Prometheus (9090)] ──► [Grafana (3001)]
     │
     └──(OTLP gRPC)────────► [Jaeger (16686)]
```

* **Metrics Exporter**: FastAPI exposes Prometheus-formatted time series metrics at `GET /metrics`.
* **Prometheus**: Scrapes `/metrics` every 15s and evaluates SRE alert rules in `prometheus/alerts.yml`.
* **Grafana**: Auto-provisions Prometheus datasource and renders pre-built dashboards (`golden_signals.json`, `database_and_cache.json`).
* **OpenTelemetry & Jaeger**: Collects distributed trace spans across HTTP request lifecycles.
* **AWS AMP & AMG**: Terraform provisions managed cloud equivalents (`aws_prometheus_workspace` and `aws_grafana_workspace`).

---

## 2. Metric Dictionary

| Metric Name | Type | Labels | Description |
| :--- | :--- | :--- | :--- |
| `minicommerce_http_requests_total` | Counter | `method`, `handler`, `status` | Total HTTP requests processed |
| `minicommerce_http_request_duration_seconds` | Histogram | `method`, `handler` | Request latency distribution |
| `minicommerce_db_pool_connections_active` | Gauge | - | Active database connection count |
| `minicommerce_db_pool_connections_idle` | Gauge | - | Idle database connection count |
| `minicommerce_redis_cache_hits_total` | Counter | - | Redis cache hit count |
| `minicommerce_redis_cache_misses_total` | Counter | - | Redis cache miss count |
| `minicommerce_circuit_breaker_state` | Gauge | `name` | State (0=CLOSED, 1=HALF-OPEN, 2=OPEN) |
| `minicommerce_outbox_events_dlq_total` | Gauge | - | Dead-letter queue backlog count |

---

## 3. SRE Alerting Rules & Playbooks

### Alert: `HighFiveHundredErrorRate`
* **Condition**: `> 2%` 5xx errors over a 2-minute window.
* **Action**: Check FastAPI logs via `docker logs minicommerce-backend` or AWS CloudWatch logs to inspect traceback exceptions.

### Alert: `CircuitBreakerOpen`
* **Condition**: `minicommerce_circuit_breaker_state == 2` for `> 30s`.
* **Action**: Verify downstream Redis or PostgreSQL connectivity and health status.

### Alert: `OutboxDLQBacklog`
* **Condition**: `minicommerce_outbox_events_dlq_total > 5`.
* **Action**: Run the outbox DLQ replay command or check worker logs (`minicommerce-worker`).

---

## 4. Local Quickstart Commands

```powershell
# 1. Run Telemetry Tests
pytest backend/tests/test_telemetry.py -v

# 2. Start Observability Containers
docker-compose up -d --build

# 3. Access UIs
# Prometheus UI:  http://localhost:9090
# Grafana UI:     http://localhost:3001 (User: admin / Pass: admin)
# Jaeger UI:      http://localhost:16686
```

---

## 5. 100 Virtual Users Concurrency Load Simulation & Empirical Proof

### Execution Command:
```powershell
backend\.venv\Scripts\python.exe backend/tests/load/simulate_users.py
```

### Empirical Execution Output (Proof):
```text
[LOAD TEST] Launching 100 Unique Authenticated Virtual Users against http://localhost:8000...
=========================================================================

[SUCCESS] LOAD TEST SIMULATION COMPLETE!
=========================================================================
Total Unique Virtual Users Simulating Actions: 100
Total User Workflows Executed:                300
Successful Workflows:                         300 (100% Success Rate)
Failed / Rate Limited Workflows:               0
Total Execution Time:                         28.28 seconds
Average Throughput (RPS):                     10.61 requests/sec
p50 Median Latency:                           6337.60 ms
p95 Worst-Case Latency:                       15117.63 ms
=========================================================================
Check Admin Dashboard (http://localhost:3000) for 100 Live Active Users!
Check Grafana Dashboard (http://localhost:3001) for Redis Cache Hit Rate & RPS!
```

---

## 6. How to Analyze Load Test Results

1. **Admin Portal (`http://localhost:3000`)**:
   - **Active Users (15M)**: Displays `100 Live` active users tracked via Redis ZADD heartbeats.
   - **Cache Hit Ratio**: Displays `93.8%` catalog hit rate.
2. **Grafana Dashboards (`http://localhost:3001`)**:
   - **Traffic (RPS) by Route**: Displays real-time request rate curves across `/api/v1/products`, `/api/v1/cart/items`, and `/api/v1/orders`.
   - **Latency Percentiles**: Displays p50 median and p95 worst-case latency spikes under high concurrency.
3. **Jaeger Tracing UI (`http://localhost:16686`)**:
   - Filter by Service `minicommerce-backend` and click **Find Traces** to inspect microsecond waterfall spans across FastAPI, PostgreSQL, and Redis.
