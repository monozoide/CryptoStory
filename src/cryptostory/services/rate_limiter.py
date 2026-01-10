"""Token bucket rate limiter for Binance API."""

from __future__ import annotations

import asyncio
import time


class RateLimiter:
    """Async token bucket limiter."""

    def __init__(self, capacity: int, refill_rate_per_sec: float) -> None:
        self._capacity = capacity
        self._tokens = float(capacity)
        self._refill_rate = refill_rate_per_sec
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> None:
        """Acquire tokens before performing a request."""
        async with self._lock:
            await self._refill()
            while self._tokens < tokens:
                await asyncio.sleep(self._sleep_duration(tokens))
                await self._refill()
            self._tokens -= tokens

    async def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        if elapsed <= 0:
            return
        self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_rate)
        self._last_refill = now

    def _sleep_duration(self, tokens: int) -> float:
        deficit = tokens - self._tokens
        if deficit <= 0:
            return 0.0
        return max(deficit / self._refill_rate, 0.01)
