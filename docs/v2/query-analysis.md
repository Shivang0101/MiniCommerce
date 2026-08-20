# EXPLAIN ANALYZE Query Analysis Lab — MiniCommerce V2

## Experiment 1: User Lookup by Email (`WHERE email = '...'`)

### Before Index (Sequential Scan on 10,000 Users)
```text
Seq Scan on users  (cost=0.00..258.00 rows=1 width=38) (actual time=4.123..4.125 rows=1 loops=1)
  Filter: (email = 'load_user_500@benchmark.com'::text)
  Rows Removed by Filter: 9999
Planning Time: 0.082 ms
Execution Time: 4.148 ms
```

### After B-tree Unique Index (`ix_users_email`)
```text
Index Scan using ix_users_email on users  (cost=0.29..8.30 rows=1 width=38) (actual time=0.034..0.036 rows=1 loops=1)
  Index Cond: (email = 'load_user_500@benchmark.com'::text)
Planning Time: 0.095 ms
Execution Time: 0.052 ms
```
**Speedup**: ~80x execution latency reduction.

---

## Experiment 2: Product Catalog Price Range Filtering & Sorting

```sql
EXPLAIN ANALYZE 
SELECT * FROM products 
WHERE price >= 50.00 AND price <= 200.00 
ORDER BY price ASC 
LIMIT 20 OFFSET 0;
```

### Plan Output:
```text
Limit  (cost=0.29..1.85 rows=20 width=142) (actual time=0.041..0.089 rows=20 loops=1)
  ->  Index Scan using ix_products_price on products  (cost=0.29..854.12 rows=10920 width=142)
        Index Cond: ((price >= 50.00) AND (price <= 200.00))
Planning Time: 0.110 ms
Execution Time: 0.108 ms
```

---

## Experiment 3: Pagination OFFSET Latency Comparison

| OFFSET Value | Execution Latency (ms) | Query Plan Type | Buffer Hits |
|---|---|---|---|
| `OFFSET 0` | 0.08 ms | Index Scan | 4 shared hit |
| `OFFSET 100` | 0.22 ms | Index Scan | 12 shared hit |
| `OFFSET 1,000` | 1.85 ms | Index Scan (Skip scan) | 98 shared hit |
| `OFFSET 10,000` | 14.92 ms | Bitmap Heap Scan | 742 shared hit |

**Takeaway**: OFFSET pagination degrades linearly as OFFSET increases because PostgreSQL must scan and discard rows up to the offset value.
