import sys
import time
import asyncio
import statistics
from pathlib import Path
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import httpx
from sqlalchemy import text
from app.db.session import AsyncSessionLocal, engine
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.product import Product

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def run_query_analysis_benchmarks():
    """Recreates the EXPLAIN ANALYZE benchmark queries documented in docs/v2/query-analysis.md."""
    print("=" * 80)
    print("1. RUNNING EXPLAIN ANALYZE BENCHMARKS (query-analysis.md)")
    print("=" * 80)

    async with AsyncSessionLocal() as session:
        # Check database engine dialect
        dialect_name = session.bind.dialect.name
        print(f"[INFO] Database Dialect: {dialect_name.upper()}")

        if dialect_name != "postgresql":
            print("[WARN] EXPLAIN ANALYZE with BUFFERS timing requires a PostgreSQL engine.")
            print("[WARN] Executing SQLite / Generic EXPLAIN plans for structure verification...")

        # Experiment 1: User Lookup by Email
        print("\n--- Experiment 1: User Lookup by Email (`WHERE email = '...'`) ---")
        try:
            res = await session.execute(
                text("EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'benchmark_test@example.com';")
                if dialect_name == "postgresql" else text("EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'benchmark_test@example.com';")
            )
            explain_lines = res.scalars().all()
            for line in explain_lines:
                print(f"  {line}")
        except Exception as e:
            print(f"  [ERROR] Could not execute EXPLAIN query: {e}")

        # Experiment 2: Product Price Range Filtering & Sorting
        print("\n--- Experiment 2: Product Catalog Price Range Filtering & Sorting ---")
        try:
            res = await session.execute(
                text("EXPLAIN ANALYZE SELECT * FROM products WHERE price >= 50.00 AND price <= 200.00 ORDER BY price ASC LIMIT 20 OFFSET 0;")
                if dialect_name == "postgresql" else text("EXPLAIN QUERY PLAN SELECT * FROM products WHERE price >= 50.00 AND price <= 200.00 ORDER BY price ASC LIMIT 20 OFFSET 0;")
            )
            explain_lines = res.scalars().all()
            for line in explain_lines:
                print(f"  {line}")
        except Exception as e:
            print(f"  [ERROR] Could not execute EXPLAIN query: {e}")

        # Experiment 3: Pagination OFFSET Bounds Latency Comparison
        print("\n--- Experiment 3: Pagination OFFSET Bounds ---")
        offsets = [0, 100, 1000, 10000]
        for off in offsets:
            start = time.perf_counter()
            try:
                await session.execute(
                    text(f"SELECT * FROM products ORDER BY id ASC LIMIT 20 OFFSET {off};")
                )
                elapsed_ms = (time.perf_counter() - start) * 1000
                print(f"  OFFSET {off:6,d} -> Query Time: {elapsed_ms:.3f} ms")
            except Exception as e:
                print(f"  OFFSET {off:6,d} -> Error: {e}")

async def run_http_endpoint_benchmarks(concurrency: int = 50, total_requests: int = 500):
    """Recreates the HTTP load test performance benchmarks documented in docs/v2/performance.md."""
    print("\n" + "=" * 80)
    print(f"2. RUNNING HTTP ENDPOINT BENCHMARKS (performance.md)")
    print(f"   Target: {BASE_URL}")
    print(f"   Concurrency: {concurrency} virtual users | Total Requests: {total_requests}")
    print("=" * 80)

    # 1. Obtain setup data (a test product ID and auth token for protected routes)
    async with AsyncSessionLocal() as session:
        # Fetch or insert dummy user
        result = await session.execute(text("SELECT id, email FROM users LIMIT 1;"))
        row = result.first()
        if row:
            test_user_id, test_email = row[0], row[1]
        else:
            print("[WARN] No users found in DB. Run `python -m app.db.seed` first.")
            return

        token = create_access_token({"sub": str(test_user_id)})

        # Fetch product ID
        p_res = await session.execute(text("SELECT id FROM products LIMIT 1;"))
        p_row = p_res.first()
        test_product_id = str(p_row[0]) if p_row else None

    headers = {"Authorization": f"Bearer {token}"}

    # Define endpoints to benchmark
    endpoints = [
        ("GET /api/v1/products (Paginated)", "GET", f"{BASE_URL}/products?page=1&page_size=20", None, {}),
    ]

    if test_product_id:
        endpoints.append(("GET /api/v1/products/{id}", "GET", f"{BASE_URL}/products/{test_product_id}", None, {}))
        endpoints.append(("POST /api/v1/cart/items", "POST", f"{BASE_URL}/cart/items", {"product_id": test_product_id, "quantity": 1}, headers))

    endpoints.append(("POST /api/v1/orders (Atomic Checkout)", "POST", f"{BASE_URL}/orders", None, headers))

    print(f"\n{'Endpoint':<40} | {'RPS':<8} | {'Avg (ms)':<9} | {'p50 (ms)':<9} | {'p95 (ms)':<9} | {'p99 (ms)':<9} | {'Error %':<7}")
    print("-" * 105)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check server health
        try:
            health_check = await client.get(f"{BASE_URL}/products?page=1&page_size=1")
            if health_check.status_code != 200:
                print(f"[ERROR] FastAPI server returned status {health_check.status_code}. Is Uvicorn running on port 8000?")
                return
        except Exception:
            print("[ERROR] Could not connect to FastAPI server at http://127.0.0.1:8000.")
            print("[HINT] Launch Uvicorn in another terminal first:\n       python -m uvicorn app.main:app --port 8000")
            return

        semaphore = asyncio.Semaphore(concurrency)

        for name, method, url, json_body, req_headers in endpoints:
            latencies = []
            errors = 0

            async def make_request(request_index: int):
                nonlocal errors
                async with semaphore:
                    # Inject unique idempotency key for checkout route
                    current_headers = dict(req_headers)
                    if "orders" in url:
                        current_headers["Idempotency-Key"] = f"bench_key_{time.time_ns()}_{request_index}"

                    start_time = time.perf_counter()
                    try:
                        if method == "GET":
                            resp = await client.get(url, headers=current_headers)
                        else:
                            resp = await client.post(url, json=json_body, headers=current_headers)

                        latency_ms = (time.perf_counter() - start_time) * 1000
                        if resp.status_code in (200, 201):
                            latencies.append(latency_ms)
                        else:
                            errors += 1
                    except Exception:
                        errors += 1

            t_start = time.perf_counter()
            tasks = [make_request(i) for i in range(total_requests)]
            await asyncio.gather(*tasks)
            total_duration = time.perf_counter() - t_start

            if latencies:
                latencies.sort()
                rps = len(latencies) / total_duration
                avg_lat = statistics.mean(latencies)
                p50 = latencies[int(len(latencies) * 0.50)]
                p95 = latencies[int(len(latencies) * 0.95)]
                p99 = latencies[int(len(latencies) * 0.99)]
                err_rate = (errors / total_requests) * 100
                print(f"{name:<40} | {rps:<8.1f} | {avg_lat:<9.1f} | {p50:<9.1f} | {p95:<9.1f} | {p99:<9.1f} | {err_rate:<7.2f}%")
            else:
                print(f"{name:<40} | FAILED (All requests returned errors)")

async def run_redis_cache_benchmarks(num_requests: int = 50):
    """Recreates the Redis Cache-Aside latency benchmarks documented in docs/v3/performance.md."""
    print("\n" + "=" * 80)
    print("3. RUNNING REDIS CACHE-ASIDE LATENCY BENCHMARKS (docs/v3/performance.md)")
    print("=" * 80)

    from app.core.redis import init_redis_pool, close_redis_pool
    from app.services.cache_service import CacheService

    await init_redis_pool()

    test_cache_key = "products:page=1:size=20:min=None:max=None:sb=name:so=asc:q=None:c=All"

    # Step 1: Force cache purge (Cache Miss baseline)
    await CacheService.invalidate_pattern("products:*")

    # Step 2: Measure Cache Miss Latency
    async with AsyncSessionLocal() as session:
        t0 = time.perf_counter()
        from app.services.product_service import ProductService
        products_miss, total_count = await ProductService.list_products(session, page=1, page_size=20)
        miss_latency_ms = (time.perf_counter() - t0) * 1000

    print(f"  Cache MISS (Supabase DB Query + Cache Set) -> Latency: {miss_latency_ms:.2f} ms | Returned: {len(products_miss)} items")

    # Step 3: Measure Repeated Cache Hit Latencies
    hit_latencies = []
    async with AsyncSessionLocal() as session:
        for _ in range(num_requests):
            t0 = time.perf_counter()
            products_hit, _ = await ProductService.list_products(session, page=1, page_size=20)
            hit_latencies.append((time.perf_counter() - t0) * 1000)

    avg_hit = statistics.mean(hit_latencies)
    hit_latencies.sort()
    p50_hit = hit_latencies[int(len(hit_latencies) * 0.50)]
    p95_hit = hit_latencies[int(len(hit_latencies) * 0.95)]
    speedup = miss_latency_ms / avg_hit if avg_hit > 0 else 0

    print(f"  Cache HIT  (Redis In-Memory Lookup, n={num_requests}) -> Avg: {avg_hit:.2f} ms | p50: {p50_hit:.2f} ms | p95: {p95_hit:.2f} ms")
    print(f"  [RESULT] Cache Hit Speedup: {speedup:.1f}x faster than database scan!")

    await close_redis_pool()

async def main():
    await run_query_analysis_benchmarks()
    await run_http_endpoint_benchmarks(concurrency=20, total_requests=100)
    await run_redis_cache_benchmarks(num_requests=50)

if __name__ == "__main__":
    asyncio.run(main())
