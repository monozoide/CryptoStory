"""Tests for RateLimiter."""

import asyncio

import pytest

from cryptostory.services.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_acquire() -> None:
    limiter = RateLimiter(capacity=2, refill_rate_per_sec=2)
    await limiter.acquire()
    await limiter.acquire()
    assert True


@pytest.mark.asyncio
async def test_rate_limiter_waits() -> None:
    limiter = RateLimiter(capacity=1, refill_rate_per_sec=1)
    await limiter.acquire()
    task = asyncio.create_task(limiter.acquire())
    await asyncio.sleep(0.2)
    assert not task.done()
    await asyncio.sleep(1.2)
    assert task.done()
