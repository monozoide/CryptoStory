"""Tests for FetchService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
import httpx

from cryptostory.domain.exceptions import CandleMismatchError, DomainException
from cryptostory.domain.value_objects import Interval
from cryptostory.services.fetch_service import FetchService
from cryptostory.services.rate_limiter import RateLimiter


@pytest.fixture()
def rate_limiter() -> RateLimiter:
    return RateLimiter(capacity=10, refill_rate_per_sec=10)


@pytest.mark.asyncio
async def test_fetch_and_store_success(rate_limiter) -> None:
    client = AsyncMock()
    candle_repo = AsyncMock()
    event_repo = AsyncMock()
    candle_repo.fetch_existing_times.return_value = {}
    candle_repo.bulk_insert.return_value = 1
    client.get_klines.return_value = [
        [1704067200000, "1", "2", "0.5", "1.5", "10"],
    ]

    service = FetchService(client, rate_limiter, candle_repo, event_repo)
    inserted = await service.fetch_and_store(
        "BTCUSDT",
        Interval.ONE_MINUTE,
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    assert inserted == 1


@pytest.mark.asyncio
async def test_fetch_and_store_dedup(rate_limiter) -> None:
    client = AsyncMock()
    candle_repo = AsyncMock()
    event_repo = AsyncMock()
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    candle_repo.fetch_existing_times.return_value = {
        now: type("Candle", (), {"close": 1.5}),
    }
    candle_repo.bulk_insert.return_value = 0
    client.get_klines.return_value = [
        [int(now.timestamp() * 1000), "1", "2", "0.5", "1.5", "10"],
    ]

    service = FetchService(client, rate_limiter, candle_repo, event_repo)
    inserted = await service.fetch_and_store("BTCUSDT", Interval.ONE_MINUTE, now, now)
    assert inserted == 0


@pytest.mark.asyncio
async def test_fetch_and_store_mismatch(rate_limiter) -> None:
    client = AsyncMock()
    candle_repo = AsyncMock()
    event_repo = AsyncMock()
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    candle_repo.fetch_existing_times.return_value = {
        now: type("Candle", (), {"close": 1.2}),
    }
    client.get_klines.return_value = [
        [int(now.timestamp() * 1000), "1", "2", "0.5", "1.5", "10"],
    ]

    service = FetchService(client, rate_limiter, candle_repo, event_repo)
    with pytest.raises(CandleMismatchError):
        await service.fetch_and_store("BTCUSDT", Interval.ONE_MINUTE, now, now)
    event_repo.add.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_retry_on_timeout(rate_limiter) -> None:
    client = AsyncMock()
    candle_repo = AsyncMock()
    event_repo = AsyncMock()
    candle_repo.fetch_existing_times.return_value = {}
    candle_repo.bulk_insert.return_value = 0
    client.get_klines.side_effect = httpx.TimeoutException("timeout")

    service = FetchService(client, rate_limiter, candle_repo, event_repo)
    with pytest.raises(DomainException):
        await service.fetch_and_store(
            "BTCUSDT",
            Interval.ONE_MINUTE,
            datetime(2024, 1, 1, tzinfo=timezone.utc),
            datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
