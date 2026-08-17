# MiniCommerce V1 — Backend Engineering Laboratory

**MiniCommerce V1** is a clean, modular backend engineering laboratory built with **FastAPI**, **PostgreSQL** (via Supabase), **SQLAlchemy 2.x ORM**, **Alembic**, **JWT Authentication**, and **Atomic Transactions**, complemented by a modern Vanilla JS Single Page Application (SPA).

---

## 🏗️ Architectural Overview

MiniCommerce strictly enforces a 4-tier separation of concerns:

```text
HTTP Request
     │
     ▼
Router Layer (Thin route handlers: app/api/v1/)
     │
     ▼
Service Layer (Business rules & Atomic transactions: app/services/)
     │
     ▼
SQLAlchemy DB Layer (ORM Models & Session: app/models/ & app/db/)
     │
     ▼
PostgreSQL / Supabase (Database persistence)
```

### Architectural Principles
1. **Thin Routers**: Route handlers only handle request parsing and response formatting.
2. **Business Logic in Services**: All business rules, validation, and transactions reside in services.
3. **Pydantic Schemas vs ORM Models**: Pydantic schemas define API contracts (`schemas/`); SQLAlchemy 2.x declarative models represent database persistence (`models/`).
4. **Atomic Checkout**: The checkout flow executes inside an explicit database transaction with stock validation, historical price snapshotting, stock reduction, and cart cleanup.

---

## 📁 Project Directory Structure

```text
MiniCommerce/
├── README.md                 # Project Overview & Guide
├── .gitignore                # Git ignore rules (.venv, secrets, caches)
├── abcd.txt                  # Step-by-step work log & error tracker
│
├── v/                        # Version Documentation Folder
│   └── v1.md                 # Version 1 Architecture & Implementation Specification
│
├── backend/                  # FastAPI Application Root
│   ├── app/
│   │   ├── api/              # API Route Handlers & Dependencies
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── products.py
│   │   │   │   ├── cart.py
│   │   │   │   ├── orders.py
│   │   │   │   └── router.py
│   │   │   └── deps.py
│   │   ├── core/             # Settings & Security (JWT, Bcrypt)
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── middleware/       # Request ID & Access Logging
│   │   │   ├── request_id.py
│   │   │   └── logging.py
│   │   ├── models/           # SQLAlchemy 2.x ORM Models
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── cart.py
│   │   │   └── order.py
│   │   ├── schemas/          # Pydantic API Schemas
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── cart.py
│   │   │   └── order.py
│   │   ├── services/         # Business Logic & Transactions
│   │   │   ├── auth_service.py
│   │   │   ├── product_service.py
│   │   │   ├── cart_service.py
│   │   │   └── order_service.py
│   │   ├── db/               # DB Session & Seed Script
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── seed.py
│   │   └── main.py           # FastAPI Application Entrypoint
│   ├── alembic/              # Database Migration Scripts
│   ├── tests/                # Pytest Unit & Integration Suite
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env
│
└── frontend/                 # Vanilla JS SPA Client
    ├── index.html            # HTML5 Layout & Modals
    ├── styles.css            # Modern Dark Glassmorphism CSS
    └── app.js                # Vanilla JS SPA Client Logic
```

---

## ⚡ Quick Start Guide

### 1. Environment Setup
```powershell
cd backend

# Create Virtual Environment
python -m venv .venv

# Activate Virtual Environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install Dependencies
pip install -r requirements.txt
```

### 2. Configure Database & Seed Data
Update `backend/.env` with your Supabase / PostgreSQL database URI:
```env
DATABASE_URL=postgresql+asyncpg://postgres.ehnadqstbnlfixhpibuu:MiniCommerceDB%40123%40123%40123@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
JWT_SECRET=supersecretkey_minicommerce_v1_laboratory_key_2026
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Run the seed script to create all database tables and insert simulated data:
```powershell
python app/db/seed.py
```

### 3. Run Pytest Suite
```powershell
python -m pytest -v
```
*Expected: 17/17 tests passing.*

### 4. Start Backend Server
```powershell
uvicorn app.main:app --reload --reload-exclude ".venv" --port 8000
```
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 5. Start Frontend SPA
In a separate terminal:
```powershell
cd frontend
python -m http.server 3000 --bind 127.0.0.1
```
- **Web App**: [http://localhost:3000](http://localhost:3000)

---

## 🔑 Default Simulated Accounts

| Role / User | Email | Password | Pre-seeded State |
|---|---|---|---|
| **User 1** | `alice@example.com` | `Password123!` | Active Cart with items |
| **User 2** | `bob@example.com` | `Password123!` | Confirmed Order history |
| **User 3** | `charlie@example.com` | `Password123!` | Clean Account |

---

## 🛠️ API Reference Summary

### Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register` — Register new user account.
- `POST /api/v1/auth/login` — Login and acquire JWT bearer access token.
- `GET /api/v1/auth/me` — Retrieve current authenticated user profile.

### Products (`/api/v1/products`)
- `GET /api/v1/products` — List all available products.
- `GET /api/v1/products/{id}` — Get single product details by ID.
- `POST /api/v1/products` — Create new product record.

### Cart (`/api/v1/cart`)
- `GET /api/v1/cart` — Get current user's shopping cart.
- `POST /api/v1/cart/items` — Add product item to cart (validates stock).
- `PATCH /api/v1/cart/items/{id}` — Update item quantity in cart.
- `DELETE /api/v1/cart/items/{id}` — Remove item from cart.

### Orders & Checkout (`/api/v1/orders`)
- `POST /api/v1/orders` — **Atomic Checkout**: Locks items, checks stock, creates order, snapshots prices, deducts stock, clears cart.
- `GET /api/v1/orders` — List user's order history.
- `GET /api/v1/orders/{id}` — Get specific order details (enforces ownership).

---

## 📝 Work Log & Error Tracker
Refer to **[abcd.txt](file:///d:/shivang/Project/MLProjects/MiniCommerce/abcd.txt)** for a step-by-step log documenting all 10 technical challenges and solutions implemented during development.
