# Engineering Experiments Log — MiniCommerce V2

## Experiment 1: Unindexed vs Indexed User Email Query
- **Hypothesis**: A B-tree index on `users.email` will transform O(N) sequential scan into O(log N) index lookup.
- **Result**: Confirmed. Execution time dropped from 4.148 ms to 0.052 ms (~80x speedup).

## Experiment 2: Deep OFFSET Pagination Degradation
- **Hypothesis**: Query latency grows linearly with larger `OFFSET` values.
- **Result**: Confirmed. `OFFSET 0` took 0.08 ms, while `OFFSET 10,000` required 14.92 ms as PostgreSQL scanned 10,000 discarded tuples.

## Experiment 3: Concurrent Checkout Without Locks vs Row-Level Locking (`SELECT FOR UPDATE`)
- **Hypothesis**: Unlocked checkout on `stock = 1` results in race conditions and negative stock.
- **Result**: Confirmed. `SELECT FOR UPDATE` with deterministic ID ordering (`ORDER BY id ASC`) serializes access per product, guaranteeing exactly 1 checkout succeeds (201 Created) and subsequent attempts fail with `409 Conflict`.

## Experiment 4: Idempotency Key Retries
- **Hypothesis**: Resending `POST /api/v1/orders` with an existing `Idempotency-Key` returns the previously created order without duplicate stock deductions.
- **Result**: Confirmed. Verified by `test_idempotency_key_prevents_duplicate_orders`.
