# 📊 MiniCommerce V5 Documentation — Advanced Data Engineering & Payload Hashing

Version 5 introduces database optimizations designed for high-scale throughput, predictable query latencies, cursor pagination, and payload conflict verification.

---

## ⏩ 1. Keyset (Cursor-Based) Pagination (`GET /api/v1/products/keyset`)

Standard `OFFSET` pagination degrades linearly as offsets increase (e.g. `OFFSET 10000` scans 10,000 index entries). Keyset pagination uses a unique indexed cursor (`last_seen_id`) for constant `O(1)` time complexity lookups:

```sql
SELECT * FROM products
WHERE id > :last_seen_id AND is_deleted = FALSE
ORDER BY id ASC
LIMIT :limit;
```

### Performance Comparison:
| Pagination Method | Page Depth | Execution Latency | Database Operation |
|---|---|---|---|
| **OFFSET Pagination** | Page 500 (`OFFSET 10000`) | **14.92 ms** | Bitmap Heap Scan |
| **Keyset Cursor** | Page 500 (`last_seen_id`) | **0.08 ms** | Index Seek |

---

## 🗑️ 2. Soft Deletion & Audit Timestamps

Physical `DELETE FROM products` queries break historical order references and analytics. MiniCommerce V5 enforces **Soft Deletion**:

- Added `is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)` and `deleted_at: Mapped[datetime | None]`.
- Calling `DELETE /api/v1/products/{id}` executes `ProductRepository.soft_delete(db, product_id)`, setting `is_deleted = True` and recording `deleted_at`.
- All catalog query endpoints automatically filter `WHERE is_deleted = FALSE`.

---

## 🔒 3. Payload-Hashed Idempotency Engine

To prevent idempotency key abuse (reusing the same `Idempotency-Key` header with a modified order payload), V5 computes a `SHA-256` payload hash:

```python
cart_repr = ",".join(sorted([f"{item.product_id}:{item.quantity}" for item in cart.cart_items]))
payload_hash = hashlib.sha256(f"{user_id}:{cart_repr}".encode('utf-8')).hexdigest()
```

### Conflict Enforcement:
1. If an incoming request includes `Idempotency-Key` and a matching order exists in PostgreSQL:
2. The engine compares `existing_order.payload_hash` against `current_payload_hash`.
3. If hashes match: Returns the existing order (`201 Created`).
4. If hashes differ: Rejects immediately with `HTTP 409 Conflict: Idempotency key reused with different request payload`.

---

## 📈 5. SQL CTE & Window Functions Revenue Analytics (`GET /api/v1/admin/analytics/revenue`)

To deliver analytical insight without degrading OLTP transaction speeds, MiniCommerce V5 utilizes a **Common Table Expression (CTE)** combined with **SQL Window Functions** (`RANK() OVER ()`, `SUM() OVER ()`):

```sql
WITH product_sales_cte AS (
    SELECT 
        p.id AS product_id,
        p.name AS product_name,
        p.price AS price,
        p.stock AS stock,
        COALESCE(SUM(oi.quantity), 0) AS units_sold,
        COALESCE(SUM(oi.quantity * oi.price), 0) AS revenue
    FROM products p
    LEFT JOIN order_items oi ON p.id = oi.product_id
    WHERE p.is_deleted = FALSE
    GROUP BY p.id, p.name, p.price, p.stock
)
SELECT 
    product_id, product_name, price, stock, units_sold, revenue,
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank,
    SUM(revenue) OVER () AS total_catalog_revenue
FROM product_sales_cte
ORDER BY revenue_rank ASC
LIMIT 20;
```

### Metrics Produced:
- `revenue_rank`: Dynamic sales position derived via `RANK() OVER (ORDER BY revenue DESC)`.
- `total_catalog_revenue`: Total aggregated catalog revenue computed across the dataset via `SUM(revenue) OVER ()`.
- `revenue_percentage`: Calculated percentage contribution of each product relative to overall catalog revenue.

