# MiniCommerce V3 — Architecture & Container Topology

## Overview

MiniCommerce V3 evolves the laboratory to include:
1. **Multi-Container Local Orchestration (`docker-compose.yml`)**:
   - `backend`: FastAPI Python 3.12-slim server (`port 8000`).
   - `redis`: Redis 7-alpine in-memory cache server (`port 6379`).
   - `frontend`: Multi-stage built React Vite SPA served via Nginx alpine (`port 3000`).
2. **Remote Supabase PostgreSQL Database**:
   - Persists all domain data in AWS Cloud PostgreSQL (409,913 records).
   - Keeps local container disk footprint lightweight.
3. **Async Redis Caching Layer**:
   - Implements Cache-Aside pattern for product catalog reads (`GET /api/v1/products`).
   - Implements Cache Invalidation pattern (`products:*` cache purge) upon order placement or new product creation.
   - Fault-tolerant fallback: automatically handles Redis unavailability/timeouts with zero HTTP 500 impact on clients.
4. **Health & Readiness Probes**:
   - `/healthz`: HTTP 200 Liveness probe for process status.
   - `/readyz`: HTTP 200/503 Readiness probe testing active DB & Redis pool connectivity.

---

## Visual Architecture Diagram (V3)

```text
               +----------------------------------------+
               |        React 18 + Vite 5 SPA           |
               |  Served via Nginx Container (Port 3000)|
               +----------------------------------------+
                                   | (HTTP REST API)
                                   v
               +----------------------------------------+
               |            FastAPI Backend             |
               |       (python:3.12-slim Port 8000)     |
               |  - Health Probes (/healthz, /readyz)   |
               +----------------------------------------+
                      /                        \
      (Cache Read/Write & Invalidate)     (SQL Persistence & Row Locks)
                    /                            \
                   v                              v
   +--------------------------------+   +------------------------------------+
   |        Redis Container         |   |    Remote Supabase PostgreSQL DB   |
   |      (redis:7-alpine 6379)     |   |     (409,913 Records on AWS)       |
   +--------------------------------+   +------------------------------------+
```
