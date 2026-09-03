"""MiniCommerce Telemetry & Observability Engine.

Exposes standard Prometheus metrics (/metrics endpoint), custom SRE operational metrics,
and configures OpenTelemetry distributed tracing.
"""

import logging
import os

from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger("minicommerce.telemetry")

# ================================================================================
# CUSTOM PROMETHEUS METRICS DEFINITIONS
# ================================================================================

# HTTP Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "minicommerce_http_requests_total",
    "Total HTTP requests received",
    ["method", "handler", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "minicommerce_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "handler"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Database Connection Pool Metrics
DB_POOL_ACTIVE = Gauge(
    "minicommerce_db_pool_connections_active",
    "Number of active database connections in connection pool",
)

DB_POOL_IDLE = Gauge(
    "minicommerce_db_pool_connections_idle",
    "Number of idle database connections in connection pool",
)

# Redis Cache Metrics
REDIS_CACHE_HITS = Counter(
    "minicommerce_redis_cache_hits_total",
    "Total number of Redis cache hits",
)

REDIS_CACHE_MISSES = Counter(
    "minicommerce_redis_cache_misses_total",
    "Total number of Redis cache misses",
)

# Asynchronous Background Worker & Outbox Metrics
ARQ_QUEUE_DEPTH = Gauge(
    "minicommerce_arq_worker_queue_depth",
    "Current depth of ARQ background worker task queue",
)

ARQ_TASKS_COMPLETED = Counter(
    "minicommerce_arq_tasks_completed_total",
    "Total background tasks completed successfully by ARQ worker",
    ["task_name"],
)

OUTBOX_PENDING = Gauge(
    "minicommerce_outbox_events_pending_total",
    "Total transactional outbox events awaiting processing",
)

OUTBOX_DLQ = Gauge(
    "minicommerce_outbox_events_dlq_total",
    "Total dead-letter queue outbox events requiring manual intervention",
)

# Circuit Breaker Metrics (0 = CLOSED, 1 = HALF-OPEN, 2 = OPEN)
CIRCUIT_BREAKER_STATE = Gauge(
    "minicommerce_circuit_breaker_state",
    "Current state of downstream circuit breaker (0=CLOSED, 1=HALF-OPEN, 2=OPEN)",
    ["name"],
)


# ================================================================================
# TELEMETRY SETUP FUNCTION
# ================================================================================


def setup_telemetry(app: FastAPI) -> Instrumentator:
    """Instruments FastAPI application with Prometheus metrics exporter and OpenTelemetry

    tracing.
    """
    logger.info("Initializing Prometheus metrics exporter...")

    # Set initial default metric values
    CIRCUIT_BREAKER_STATE.labels(name="redis_cache").set(0)
    OUTBOX_PENDING.set(0)
    OUTBOX_DLQ.set(0)
    REDIS_CACHE_HITS.inc(0)
    REDIS_CACHE_MISSES.inc(0)

    # Initialize Prometheus Instrumentator
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
    )

    # Add standard default metrics & expose /metrics endpoint
    instrumentator.instrument(app).expose(app, endpoint="/metrics", tags=["telemetry"])

    # Optional: Setup OpenTelemetry Distributed Tracing if enabled
    _setup_opentelemetry(app)

    logger.info("Prometheus metrics successfully exposed on endpoint /metrics")
    return instrumentator


def _setup_opentelemetry(app: FastAPI) -> None:
    """Configures OpenTelemetry tracer provider and OTLP exporter if OTEL endpoint is set."""
    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not otel_endpoint:
        logger.info("OTEL_EXPORTER_OTLP_ENDPOINT not configured. Skipping OpenTelemetry tracing.")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": "minicommerce-backend"})
        provider = TracerProvider(resource=resource)
        endpoint_clean = otel_endpoint.replace("http://", "").replace("https://", "")
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint_clean, insecure=True))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
        logger.info(f"OpenTelemetry tracing enabled with exporter endpoint: {endpoint_clean}")
    except Exception as exc:
        logger.warning(f"Unable to initialize OpenTelemetry tracing: {exc}")


def record_cache_hit() -> None:
    """Increments Redis cache hit counter."""
    REDIS_CACHE_HITS.inc()


def record_cache_miss() -> None:
    """Increments Redis cache miss counter."""
    REDIS_CACHE_MISSES.inc()


def update_circuit_breaker_state(name: str, state_val: int) -> None:
    """Updates circuit breaker state gauge (0=CLOSED, 1=HALF-OPEN, 2=OPEN)."""
    CIRCUIT_BREAKER_STATE.labels(name=name).set(state_val)
