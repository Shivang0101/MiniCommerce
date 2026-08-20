# Database Indexing Strategy — MiniCommerce V2

## Evaluated Query Patterns & Index Placement

| Table | Targeted Query Pattern | Index Definition | Index Type |
|---|---|---|---|
| `users` | `WHERE email = ?` | `ix_users_email` | B-tree Unique |
| `carts` | `WHERE user_id = ?` | `ix_carts_user_id` | B-tree Unique |
| `cart_items` | `WHERE cart_id = ?` | `ix_cart_items_cart_id` | B-tree Foreign Key |
| `cart_items` | `WHERE cart_id = ? AND product_id = ?` | `uq_cart_product` | B-tree Composite Unique |
| `orders` | `WHERE user_id = ? ORDER BY created_at DESC` | `ix_orders_user_id` | B-tree Foreign Key |
| `orders` | `WHERE user_id = ? AND idempotency_key = ?` | `uq_user_idempotency_key` | B-tree Composite Unique |
| `order_items` | `WHERE order_id = ?` | `ix_order_items_order_id` | B-tree Foreign Key |
| `products` | `WHERE price >= ? AND price <= ? ORDER BY price ASC` | `ix_products_price` | B-tree Range |
| `products` | `ORDER BY created_at DESC` | `ix_products_created_at` | B-tree Bounded |

## Design Rules for Indexes
1. **High Selectivity**: Unique columns (`email`, `idempotency_key`) yield single-row index scans.
2. **Foreign Key Joins**: Every foreign key column (`user_id`, `cart_id`, `order_id`, `product_id`) is indexed to accelerate JOIN queries and cascade deletions.
3. **Prevent Duplicate Work**: Indexes are managed exclusively via Alembic migrations.
