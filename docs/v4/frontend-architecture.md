# Version 4 Frontend & Observability Dashboard Architecture

This document details the architectural design, component topology, and visual layout of the **MiniCommerce V4 Professional Storefront** and **Enterprise Admin Observability Control Center**.

---

## 🛒 1. Professional E-Commerce Storefront Architecture (Amazon / BestBuy Style)

The Storefront UI is structured into modular, responsive React 18 components designed to deliver a high-converting, authentic retail experience:

```
[App.jsx]
 ├── [Navbar.jsx] ──────────── Brand Logo, "Deliver to" Location, Search Bar, Rate Quota, Cart Badge
 ├── [HeroBanner.jsx] ──────── Promotional Deal Carousel, Category Quick Links, Shipping Perks
 ├── [CategoryBar.jsx] ────── Category Filter Pills (Keyboards, Monitors, Audio, Storage, Components)
 ├── [ControlBar.jsx] ────── Price Range Filters, Sort By, Items Per Page Selector
 ├── [ProductGrid.jsx] ────── Responsive Grid Container
 │    └── [ProductCard.jsx] ── Category Icon Visual, Brand Tag, Star Ratings, Discount %, MSRP Strikethrough, Prime Badge
 ├── [Pagination.jsx] ────── Page Navigation
 └── [CartDrawer.jsx] ────── Item Thumbnails, Quantity Selectors, Order Summary, Real-Time Task Progress Timeline
```

### Component Highlights:
- **`HeroBanner.jsx`**: Displays promotional banners ("Tech Deals Week — Up to 40% Off") and service highlights (FREE Express Shipping, 2-Year Hardware Protection, Async Task Checkout).
- **`ProductCard.jsx`**: Displays category-specific visual icon boxes, star ratings (`★★★★½ 4.8 (248)`), MSRP strikethroughs with discount badges (`$120.00` ~~$149.99~~ `18% OFF`), Express shipping badges, and stock availability tags.
- **`Navbar.jsx`**: Amazon-style header featuring a "Deliver to New York 10001" location pill, live Rate Limit Quota meter, Admin Panel toggle, Notification Inbox bell, and Cart count badge.

---

## 📊 2. Enterprise Admin Observability Control Center (Datadog / Grafana Style)

The Admin Dashboard provides real-time system health, telemetry metrics, and distributed span tracing for site reliability engineers (SREs) and platform administrators:

```
[AdminDashboard.jsx]
 ├── [Global System Status Bar] ─ Live Status: PostgreSQL, Redis 7 (1.2ms), ARQ Worker, Rate Limiter
 ├── [Top 4 KPI Metrics Grid] ── Active 15m Users, p95 API Latency, ARQ Worker Tasks, Cache Hit %
 ├── [OpenTelemetry Waterfall] ─ Multi-Span Hierarchy Timeline Tree with Microsecond Span Durations
 ├── [ARQ Worker Stream] ────── Real-Time Task Log (send_receipt_email, audit_low_stock, record_analytics)
 ├── [API Audit Stream] ──────── HTTP Transaction Audit Log (Method, Endpoint, Status Code, Latency)
 └── [Admin User Management] ── Role Grant & Promotion Modal (`POST /api/v1/admin/users`)
```

### Observability Features:
1. **System Operational Status Bar**: Monitors live connectivity and response latencies across PostgreSQL, Redis 7, ARQ Worker, and Rate Limiting middleware.
2. **OpenTelemetry-Style Distributed Waterfall Trace Visualizer**: Renders parent-child span timelines for checkout HTTP transactions (`POST /orders` ➔ `SELECT FOR UPDATE` ➔ `INSERT order` ➔ `ARQ Enqueue` ➔ `Background Execution`).
3. **ARQ Worker Task Stream**: Displays background task executions, job statuses (`COMPLETED`, `RETRY`, `FAILED`), order IDs, and execution durations in milliseconds.
4. **API Transaction Audit Stream**: Logs all incoming HTTP requests with status code badges and latency metrics.
5. **Admin Access Control**: Secured login gate requiring admin role (`is_admin: true`), with role creation and promotion capabilities.
