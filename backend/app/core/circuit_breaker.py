import asyncio
import logging
import time
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:
    def __init__(
        self,
        name: str = "default",
        failure_threshold: float = 0.5,
        recovery_time_seconds: float = 15.0,
        window_seconds: float = 10.0,
        min_requests: int = 5,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_time_seconds = recovery_time_seconds
        self.window_seconds = window_seconds
        self.min_requests = min_requests

        self.state = CircuitState.CLOSED
        self.failures: list[float] = []
        self.successes: list[float] = []
        self.last_state_change = time.time()
        self._lock = asyncio.Lock()

    def _clean_window(self, now: float):
        cutoff = now - self.window_seconds
        self.failures = [t for t in self.failures if t >= cutoff]
        self.successes = [t for t in self.successes if t >= cutoff]

    async def can_execute(self) -> bool:
        async with self._lock:
            now = time.time()
            if self.state == CircuitState.OPEN:
                if now - self.last_state_change >= self.recovery_time_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.last_state_change = now
                    self._update_telemetry()
                    logger.info(
                        f"Circuit Breaker '{self.name}' transitioning from OPEN -> HALF_OPEN"
                    )
                    return True
                return False
            return True

    def _update_telemetry(self):
        try:
            from app.core.telemetry import update_circuit_breaker_state

            val_map = {CircuitState.CLOSED: 0, CircuitState.HALF_OPEN: 1, CircuitState.OPEN: 2}
            update_circuit_breaker_state(self.name, val_map.get(self.state, 0))
        except Exception:
            pass

    async def record_success(self):
        async with self._lock:
            now = time.time()
            self._clean_window(now)
            self.successes.append(now)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.last_state_change = now
                self._update_telemetry()
                logger.info(
                    f"Circuit Breaker '{self.name}' transitioning from HALF_OPEN -> CLOSED (Recovered)"
                )

    async def record_failure(self):
        async with self._lock:
            now = time.time()
            self._clean_window(now)
            self.failures.append(now)
            total = len(self.failures) + len(self.successes)

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.last_state_change = now
                self._update_telemetry()
                logger.warning(
                    f"Circuit Breaker '{self.name}' failed in HALF_OPEN -> Tripping to OPEN"
                )
            elif self.state == CircuitState.CLOSED and total >= self.min_requests:
                fail_rate = len(self.failures) / total
                if fail_rate >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    self.last_state_change = now
                    self._update_telemetry()
                    logger.warning(
                        f"Circuit Breaker '{self.name}' failure rate {fail_rate:.2f} >= threshold {self.failure_threshold:.2f} -> Tripping to OPEN for {self.recovery_time_seconds}s"
                    )

    async def call(self, func, *args, **kwargs):
        if not await self.can_execute():
            raise CircuitBreakerOpenException(
                f"Circuit Breaker '{self.name}' is OPEN. Call rejected."
            )
        try:
            result = await func(*args, **kwargs)
            await self.record_success()
            return result
        except Exception as e:
            await self.record_failure()
            raise e


# Global Circuit Breakers for DB and Redis
db_circuit_breaker = CircuitBreaker("database_circuit_breaker")
redis_circuit_breaker = CircuitBreaker("redis_circuit_breaker")
