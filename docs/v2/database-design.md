# Database Design & Schema Specification — MiniCommerce V2

## Relational Schema

```text
+-------------------+       +-------------------+       +-------------------+
|       users       |       |       carts       |       |    cart_items     |
+-------------------+       +-------------------+       +-------------------+
| id (PK, UUID)     |<----1-| id (PK, UUID)     |<----1-| id (PK, UUID)     |
| email (UQ, String)|       | user_id (FK, UQ)  |       | cart_id (FK)      |
| password_hash     |       | created_at        |       | product_id (FK)   |
| created_at        |       | updated_at        |       | quantity (> 0)    |
+-------------------+       +-------------------+       +-------------------+
          |                                                       |
          | 1                                                     | N
          v                                                       v
+-------------------+                                   +-------------------+
|      orders       |                                   |     products      |
+-------------------+                                   +-------------------+
| id (PK, UUID)     |                                   | id (PK, UUID)     |
| user_id (FK)      |                                   | name (String)     |
| idempotency_key   |<----------------------------------| price (>= 0)      |
| status (String)   |                                   | stock (>= 0)      |
| total_amount      |                                   | created_at        |
| created_at        |                                   +-------------------+
+-------------------+                                             ^
          |                                                       |
          | 1                                                     |
          v                                                       | N
+-------------------+                                             |
|    order_items    |---------------------------------------------+
+-------------------+
| id (PK, UUID)     |
| order_id (FK)     |
| product_id (FK)   |
| quantity (> 0)    |
| price (Snapshot)  |
+-------------------+
```

## Database Constraints & Invariants

1. `products.price >= 0` (`CheckConstraint`)
2. `products.stock >= 0` (`CheckConstraint`)
3. `cart_items.quantity > 0` (`CheckConstraint`)
4. `(cart_id, product_id)` UNIQUE (`UniqueConstraint`)
5. `(user_id, idempotency_key)` UNIQUE (`UniqueConstraint` on `orders`)
