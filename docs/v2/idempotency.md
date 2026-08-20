# Idempotency Engine — MiniCommerce V2

## Objective
Prevent duplicate order creation and double stock deduction when network timeouts or client retries trigger duplicate `POST /api/v1/orders` requests.

## Implementation Architecture

```text
Client Request: POST /api/v1/orders
Header: Idempotency-Key: "idemp_1724175000_abc123"
                  │
                  ▼
         Check OrderRepository:
 WHERE user_id = ? AND idempotency_key = ?
                  │
       ┌──────────┴──────────┐
       │                     │
  [Key Found]          [Key Not Found]
       │                     │
Return Existing        Execute Atomic
Order (HTTP 201)       Checkout & Save
                       Key in Order Row
```

## Database Enforcement
Idempotency is authoritatively enforced at the database level by a unique composite constraint:

```sql
ALTER TABLE orders ADD CONSTRAINT uq_user_idempotency_key UNIQUE (user_id, idempotency_key);
```

If concurrent duplicate requests arrive simultaneously, the database constraint rejects the second insertion with a unique constraint violation, causing a safe rollback.
