# Concurrency Control & Row-Level Locking — MiniCommerce V2

## Race Conditions in E-Commerce Checkout

Under high concurrent traffic, multiple users may attempt to purchase the final remaining inventory item (`stock = 1`) simultaneously.

Without concurrency control:
1. User A reads `stock = 1`.
2. User B reads `stock = 1`.
3. User A decrements stock to 0 and creates Order A.
4. User B decrements stock to -1 (or 0) and creates Order B.
5. Result: **Overselling / Data Corruption**.

## Solution: PostgreSQL Row-Level Locking (`SELECT FOR UPDATE`)

In MiniCommerce V2, checkout uses explicit row-level locks via `ProductRepository.get_by_ids_for_update()`:

```sql
SELECT * FROM products 
WHERE id IN ('...') 
ORDER BY id ASC 
FOR UPDATE;
```

### Key Mechanisms:
1. **Pessimistic Locking**: `FOR UPDATE` locks the target product rows at the database level until the transaction finishes (`COMMIT` or `ROLLBACK`).
2. **Deterministic Locking Order**: Product IDs are sorted (`ORDER BY id ASC`) before applying `FOR UPDATE`. This prevents cyclic dependency deadlocks when two transactions request the same set of products in different order.
3. **Transaction Scope**: Stock validation and deduction execute while holding the lock. If stock is insufficient, `HTTP 409 Conflict` is returned and transaction rolls back safely.
