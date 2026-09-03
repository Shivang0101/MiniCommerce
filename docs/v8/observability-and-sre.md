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
