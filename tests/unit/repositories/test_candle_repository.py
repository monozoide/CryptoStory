"""Tests for CandleRepository."""

from datetime import datetime, timezone

import pytest

from cryptostory.domain.models import Candle
from cryptostory.domain.value_objects import Interval
from cryptostory.repositories.candle_repository import CandleRepository
from tests.unit.repositories.conftest import fake_result


class FakeExecuteResult:
    def __init__(self, rowcount: int | None) -> None:
        self.rowcount = rowcount


@pytest.mark.asyncio
async def test_bulk_insert_empty(async_session) -> None:
    repo = CandleRepository(async_session)
    assert await repo.bulk_insert([]) == 0


@pytest.mark.asyncio
async def test_bulk_insert_returns_rowcount(async_session) -> None:
    repo = CandleRepository(async_session)
    async_session.execute.return_value = FakeExecuteResult(2)
    candle = Candle(
        symbol="BTCUSDT",
        interval=Interval.ONE_MINUTE,
        time=datetime(2024, 1, 1, tzinfo=timezone.utc),
        open=1.0,
        high=1.5,
        low=0.9,
        close=1.2,
        volume=10.0,
    )
    assert await repo.bulk_insert([candle]) == 2


@pytest.mark.asyncio
async def test_fetch_range(async_session) -> None:
    repo = CandleRepository(async_session)
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    model = type("Model", (), {
        "symbol": "BTCUSDT",
        "interval": Interval.ONE_MINUTE,
        "time": now,
        "open": 1.0,
        "high": 1.5,
        "low": 0.9,
        "close": 1.2,
        "volume": 10.0,
        "created_at": now,
        "updated_at": now,
        "created_by": "system",
    })
    async_session.execute.return_value = fake_result([model])
    candles = await repo.fetch_range("BTCUSDT", Interval.ONE_MINUTE, now, now)
    assert len(candles) == 1


@pytest.mark.asyncio
async def test_fetch_existing_times(async_session) -> None:
    repo = CandleRepository(async_session)
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    model = type("Model", (), {
        "symbol": "BTCUSDT",
        "interval": Interval.ONE_MINUTE,
        "time": now,
        "open": 1.0,
        "high": 1.5,
        "low": 0.9,
        "close": 1.2,
        "volume": 10.0,
        "created_at": now,
        "updated_at": now,
        "created_by": "system",
    })
    async_session.execute.return_value = fake_result([model])
    existing = await repo.fetch_existing_times("BTCUSDT", Interval.ONE_MINUTE, [now])
    assert now in existing
