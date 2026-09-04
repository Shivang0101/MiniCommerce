import asyncio
import sys
import time
import uuid
from pathlib import Path

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import httpx
from app.core.security import create_access_token



async def run_chaos_experiment(
    target_url: str = "http://localhost:8000",
    total_requests: int = 150,
    concurrency: int = 15,
):
    print("=" * 80)
    print("      MINICOMMERCE V9 - CHAOS ENGINEERING & RESILIENCE STRESS TEST      ")
    print("=" * 80)
    print(f"Target URL:        {target_url}")
    print(f"Total Workflows:   {total_requests}")
    print(f"Concurrency Level: {concurrency}")
    print("-" * 80)

    results = {
        "successful": 0,
        "failed": 0,
        "cache_fallbacks": 0,
        "latencies_ms": [],
        "status_codes": {},
    }

    start_time = time.time()
    semaphore = asyncio.Semaphore(concurrency)

    async def worker(request_id: int):
        async with semaphore:
            async with httpx.AsyncClient(timeout=10.0) as client:
                user_id = str(uuid.uuid4())
                token = create_access_token(subject=user_id)
                headers = {"Authorization": f"Bearer {token}"}

                req_start = time.time()
                try:
                    # 1. Hit Read-Replica / Cache Catalog Endpoint
                    resp = await client.get(f"{target_url}/api/v1/products/keyset?limit=10", headers=headers)
                    duration_ms = (time.time() - req_start) * 1000.0
                    results["latencies_ms"].append(duration_ms)

                    status = resp.status_code
                    results["status_codes"][status] = results["status_codes"].get(status, 0) + 1

                    if status == 200:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1

                    # 2. Probe System Readiness
                    readiness_resp = await client.get(f"{target_url}/healthz/readiness")
                    if readiness_resp.status_code == 200:
                        results["cache_fallbacks"] += 1

                except Exception as exc:
                    results["failed"] += 1
                    print(f"[CHAOS REQ {request_id}] Failed with exception: {exc}")

    tasks = [worker(i) for i in range(total_requests)]
    await asyncio.gather(*tasks)

    total_duration = time.time() - start_time
    avg_rps = total_requests / total_duration if total_duration > 0 else 0
    latencies = sorted(results["latencies_ms"])

    p50 = latencies[int(len(latencies) * 0.5)] if latencies else 0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0

    print("\n" + "=" * 80)
    print("                      CHAOS TEST EXPERIMENT RESULTS                     ")
    print("=" * 80)
    print(f"Total Workflows Executed: {total_requests}")
    print(f"Successful Workflows:    {results['successful']}")
    print(f"Failed Workflows (500s): {results['failed']}")
    print(f"Total Execution Time:    {total_duration:.2f} seconds")
    print(f"Average Throughput:      {avg_rps:.2f} RPS")
    print(f"p50 Median Latency:      {p50:.2f} ms")
    print(f"p95 Latency:             {p95:.2f} ms")
    print(f"Status Code Summary:     {results['status_codes']}")
    print("=" * 80)

    assert results["failed"] == 0, f"Chaos test failed: {results['failed']} requests returned errors!"
    print("\n[PASSED] CHAOS EXPERIMENT COMPLETE! 0% HTTP 500 Failures under load.")


if __name__ == "__main__":
    asyncio.run(run_chaos_experiment())
