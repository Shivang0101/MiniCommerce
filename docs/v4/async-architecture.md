# Asynchronous Task Queue Architecture (ARQ & Redis)

## Executive Summary
In Version 4 of **MiniCommerce**, non-critical side effects that previously ran synchronously during the checkout HTTP transaction—such as receipt generation, stock threshold audits, and analytics metric logging—have been decoupled using an asynchronous producer-consumer pattern powered by **ARQ** and **Redis**.

---

## Architecture Topology

```
[ Client Request ]
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ FastAPI HTTP Endpoint (/api/v1/orders)                  │
│  - Select For Update Row Locks                         │
│  - DB Order Creation & Stock Deduction                  │
│  - Atomic DB Commit                                     │
└────────────────────────────┬────────────────────────────┘
                             │
            Post-Commit      │ Enqueue Job
                             ▼
┌─────────────────────────────────────────────────────────┐
│ Redis In-Memory Queue (arq:queue)                       │
└────────────────────────────┬────────────────────────────┘
                             │
            Pop & Execute    │ Worker Loop
                             ▼
┌─────────────────────────────────────────────────────────┐
│ ARQ Worker Service (minicommerce-worker)                │
│  ├── send_receipt_email(order_id, user_email, amount)   │
│  ├── audit_low_stock(product_items)                     │
│  └── record_analytics_event(event_type, payload)        │
└─────────────────────────────────────────────────────────┘
```

---

## Job Schemas & Task Definitions

### 1. `send_receipt_email`
- **Purpose**: Generates simulated email transaction receipts.
- **Parameters**: `order_id` (str), `user_email` (str), `total_amount` (str).
- **Deduplication Job ID**: `_job_id=f"email_{order.id}"`.
- **Side Effect**: Updates `order_status:{id}` state in Redis and appends notification to `user_notifications:{user_email}`.

### 2. `audit_low_stock`
- **Purpose**: Inspects remaining stock levels for items purchased in checkout.
- **Parameters**: `product_items` (list of dicts containing `product_id`, `name`, `remaining_stock`).
- **Deduplication Job ID**: `_job_id=f"stock_{order.id}"`.
- **Side Effect**: Flags items with stock <= 5 in `low_stock_alert:{product_id}` and pushes to global notifications.

### 3. `record_analytics_event`
- **Purpose**: Records order metrics without holding open database locks.
- **Parameters**: `event_type` (str), `payload` (dict).
- **Side Effect**: Increments `analytics:total_revenue` and `analytics:total_orders` in Redis.

---

## Fault Tolerance & Fallback Behavior
- **Transient Failures**: Configured with `TASK_MAX_RETRIES = 3` and exponential backoff.
- **Redis Outage**: If the Redis queue pool is unreachable, `OrderService` logs a warning and completes the HTTP checkout successfully without throwing a 500 error to the client.
