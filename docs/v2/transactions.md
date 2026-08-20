# Transactions & Isolation Levels — MiniCommerce V2

## ACID Invariants in Atomic Checkout

1. **Atomicity**: The checkout transaction either executes completely (stock deduction, order creation, order_items insertion, cart clearance) or rolls back 100% without leaving orphaned data.
2. **Consistency**: Database invariants (`stock >= 0`, `price >= 0`, `quantity > 0`) are guaranteed at all times by PostgreSQL check constraints.
3. **Isolation**: Concurrently executing checkouts cannot observe uncommitted transient stock deductions.
4. **Durability**: Upon `COMMIT`, transaction data is flushed to persistent storage.

## PostgreSQL Isolation Levels

| Isolation Level | Dirty Reads | Non-Repeatable Reads | Phantom Reads | Serialization Anomalies |
|---|---|---|---|---|
| **Read Committed** (Default) | Prevented | Allowed | Allowed | Allowed |
| **Repeatable Read** | Prevented | Prevented | Prevented | Allowed |
| **Serializable** | Prevented | Prevented | Prevented | Prevented |

In MiniCommerce V2 under **Read Committed**, row-level locking (`SELECT ... FOR UPDATE`) explicitly prevents lost updates and race conditions during stock mutations.
