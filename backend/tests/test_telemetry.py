"""Automated Pytest Suite for MiniCommerce Observability & Telemetry Engine."""

import pytest
from app.core.telemetry import (
    CIRCUIT_BREAKER_STATE,
    REDIS_CACHE_HITS,
    REDIS_CACHE_MISSES,
    record_cache_hit,
    record_cache_miss,
    update_circuit_breaker_state,
)
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint_returns_200(client: AsyncClient):
    """Verifies GET /metrics returns HTTP 200 OK and Prometheus metric exposition format."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    content = response.text
    assert "minicommerce" in content or "http_requests" in content or "python_gc" in content


@pytest.mark.asyncio
async def test_record_cache_hits_and_misses(client: AsyncClient):
    """Verifies Redis cache hit and miss functions increment Prometheus counters."""
    initial_hits = REDIS_CACHE_HITS._value.get()
    initial_misses = REDIS_CACHE_MISSES._value.get()

    record_cache_hit()
    record_cache_miss()
    record_cache_hit()

    assert REDIS_CACHE_HITS._value.get() == initial_hits + 2
    assert REDIS_CACHE_MISSES._value.get() == initial_misses + 1

    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "minicommerce_redis_cache_hits_total" in response.text
    assert "minicommerce_redis_cache_misses_total" in response.text


@pytest.mark.asyncio
async def test_circuit_breaker_state_gauge(client: AsyncClient):
    """Verifies circuit breaker state gauge updates accurately (0=CLOSED, 1=HALF-OPEN,

    2=OPEN).
    """
    update_circuit_breaker_state("redis_cache", 2)
    assert CIRCUIT_BREAKER_STATE.labels(name="redis_cache")._value.get() == 2

    update_circuit_breaker_state("redis_cache", 0)
    assert CIRCUIT_BREAKER_STATE.labels(name="redis_cache")._value.get() == 0

    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "minicommerce_circuit_breaker_state" in response.text
