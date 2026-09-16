# 🚀 MiniCommerce — AWS EC2 Single-Node Live Deployment Guide

> **Live Production Demo Environment**  
> **Instance Type**: AWS EC2 (`c7i-flex.large` / `t3.medium`, Ubuntu 24.04 LTS)  
> **Public IP Address**: `13.233.74.197`  
> **Container Stack**: 6 Docker Compose microservices (FastAPI, React SPA, ARQ Worker, Redis, Prometheus, Grafana, Jaeger)  
> **Database Scale**: 409,811+ Records (10,000 Users, 50,000 Products, 100,000 Orders, 249,811 Order Items)

---

## 🌐 Live Access Endpoints & URLs

| Service / Tool | Public URL | Description | Default Credentials |
| :--- | :--- | :--- | :--- |
| **🛒 React Storefront SPA** | [http://13.233.74.197:3000](http://13.233.74.197:3000) | Full E-Commerce UI with Catalog & Cart | *See Accounts Below* |
| **⚡ FastAPI Swagger API Docs** | [http://13.233.74.197:3000/docs](http://13.233.74.197:3000/docs) | Interactive REST API Documentation | Bearer JWT Token |
| **📊 Grafana Dashboard** | [http://13.233.74.197:3001](http://13.233.74.197:3001) | Real-time RPS, Latency (p50/p95), Cache Hits | `admin` / `admin` |
| **📈 Prometheus Metrics** | [http://13.233.74.197:9090](http://13.233.74.197:9090) | Telemetry Time-Series Exporter Engine | None |
| **🔍 Jaeger Distributed Tracing** | [http://13.233.74.197:16686](http://13.233.74.197:16686) | End-to-End Async Tracing & Latency Spans | None |
| **💚 Liveness Probe** | [http://13.233.74.197:3000/healthz](http://13.233.74.197:3000/healthz) | Health Check Endpoint | None |

---

## 🔐 Pre-Configured Demo Accounts & Credentials

### 1. SRE / System Administrator
* **Role**: Admin Panel, System Telemetry, Store Manager Catalog Mutator
* **Email**: `admin@minicommerce.com`
* **Password**: `Admin@123456`

### 2. Customer Demo Accounts (One-Click Login on UI)
* **Alice**: `alice@example.com` / `Password123!`
* **Bob**: `bob@example.com` / `Password123!`
* **Charlie**: `charlie@example.com` / `Password123!`

---

## 🛠️ EC2 Remote Management & Deployment Instructions

### SSH Remote Access
```bash
ssh -i "mini-commerce-key.pem" ubuntu@13.233.74.197
```

### Full Deployment & Environment Initialization
Execute these commands on your EC2 terminal:

```bash
# 1. Navigate to project repository
cd ~/MiniCommerce

# 2. Update code to latest release
git pull

# 3. Create backend environment configuration
cat << 'EOF' > backend/.env
DATABASE_URL=sqlite+aiosqlite:////app/minicommerce.db
JWT_SECRET=supersecretkey_minicommerce_v10_laboratory_key_2026
REDIS_URL=redis://redis:6379/0
EOF

# 4. Build and start all 6 Docker containers
docker compose up -d --build

# 5. Seed baseline demo accounts & 50,000 product catalog
docker exec -it minicommerce-backend python app/db/seed.py
docker exec -it minicommerce-backend python app/db/generate_load_data.py

# 6. Flush Redis cache to ensure fresh data lookups
docker exec -it minicommerce-redis redis-cli FLUSHALL
```

---

## 📈 Generating Live Traffic Spikes for Grafana Video Recordings

To generate real-time metrics, Redis cache hits, and latency curves on the **Grafana Dashboard (`:3001`)** during video recordings:

```bash
# Run 100 concurrent virtual user workflow load simulator against EC2
python3 backend/tests/load/simulate_users.py
```

---

## 🛡️ AWS Security Group Inbound Rules Summary

Security Group ID: `sg-061c515cb9f8e874e` (`launch-wizard-5`)

| Protocol | Port | Source | Purpose |
| :--- | :--- | :--- | :--- |
| **TCP** | `22` | `0.0.0.0/0` | SSH Terminal Access |
| **TCP** | `3000` | `0.0.0.0/0` | React Storefront SPA & Nginx Reverse Proxy |
| **TCP** | `8000` | `0.0.0.0/0` | FastAPI Backend API Direct Port |
| **TCP** | `3001` | `0.0.0.0/0` | Grafana Observability Dashboard |
| **TCP** | `9090` | `0.0.0.0/0` | Prometheus Time-Series Server |
| **TCP** | `16686` | `0.0.0.0/0` | Jaeger OpenTelemetry Tracing UI |
