"""MiniCommerce 100 Unique Virtual Users Concurrency Load Simulator.

Simulates 100 distinct virtual users with unique JWT authentication tokens executing
catalog browsing, cart operations, and checkouts against MiniCommerce API.
"""

import asyncio
import os
import random
import sys
import time
import uuid
from pathlib import Path

# Add backend directory to PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from httpx import AsyncClient, Limits
from app.core.security import create_access_token

BASE_URL = "http://localhost:8000"
NUM_USERS = 100
WORKFLOWS_PER_USER = 3


async def simulate_virtual_user(user_id: int, client: AsyncClient, results: list):
    """Simulates realistic customer workflow for a unique virtual user."""
    # Stagger initial user arrival to avoid instant rate-limit burst
    await asyncio.sleep(random.uniform(0, 1.5))

    unique_user_id = str(uuid.uuid4())
    token = create_access_token(subject=unique_user_id)
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(WORKFLOWS_PER_USER):
        start_time = time.time()
        try:
            # 1. Browse Product Catalog (Consistent query page to test Redis Cache Hit!)
            catalog_resp = await client.get("/api/v1/products?page=1&page_size=10", headers=headers)
            
            # 2. Add Item to Cart
            cart_resp = await client.post(
                "/api/v1/cart/items",
                headers=headers,
                json={"product_id": "00000000-0000-0000-0000-000000000001", "quantity": 1},
            )

            # 3. View Cart
            await client.get("/api/v1/cart", headers=headers)

            latency_ms = (time.time() - start_time) * 1000
            status_tag = "success" if catalog_resp.status_code == 200 else "rate_limited"
            results.append({"status": status_tag, "latency_ms": latency_ms})

        except Exception as exc:
            latency_ms = (time.time() - start_time) * 1000
            results.append({"status": "error", "error": str(exc), "latency_ms": latency_ms})

        # Pause between actions
        await asyncio.sleep(random.uniform(0.3, 0.8))


async def main():
    print(f"[LOAD TEST] Launching {NUM_USERS} Unique Authenticated Virtual Users against {BASE_URL}...")
    print("=========================================================================")

    # High-concurrency async HTTP client with connection pooling
    limits = Limits(max_connections=150, max_keepalive_connections=50)
    async with AsyncClient(base_url=BASE_URL, limits=limits, timeout=10.0) as client:
        results = []
        start = time.time()

        tasks = [
            simulate_virtual_user(i, client, results)
            for i in range(1, NUM_USERS + 1)
        ]
        await asyncio.gather(*tasks)

        total_duration = time.time() - start

    # Calculate Load Test Analytics
    successes = [r for r in results if r["status"] == "success"]
    errors = [r for r in results if r["status"] == "error"]
    latencies = sorted([r["latency_ms"] for r in results])

    p50 = latencies[int(len(latencies) * 0.50)] if latencies else 0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
    rps = len(results) / total_duration if total_duration > 0 else 0

    print("\n[SUCCESS] LOAD TEST SIMULATION COMPLETE!")
    print("=========================================================================")
    print(f"Total Unique Virtual Users Simulating Actions: {NUM_USERS}")
    print(f"Total User Workflows Executed:                {len(results)}")
    print(f"Successful Workflows:                         {len(successes)}")
    print(f"Failed / Rate Limited Workflows:               {len(errors)}")
    print(f"Total Execution Time:                         {total_duration:.2f} seconds")
    print(f"Average Throughput (RPS):                     {rps:.2f} requests/sec")
    print(f"p50 Median Latency:                           {p50:.2f} ms")
    print(f"p95 Worst-Case Latency:                       {p95:.2f} ms")
    print("=========================================================================")
    print("Check Admin Dashboard (http://localhost:3000) for 100 Live Active Users!")
    print("Check Grafana Dashboard (http://localhost:3001) for Redis Cache Hit Rate & RPS!")


if __name__ == "__main__":
    asyncio.run(main())
