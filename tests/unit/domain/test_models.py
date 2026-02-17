"""Tests for domain models."""

from datetime import datetime, timezone

import pytest

from cryptostory.domain.exceptions import InvalidTimestampRangeError
from cryptostory.domain.models import Candle, FetchJob, Symbol
from cryptostory.domain.value_objects import ExchangeType, Interval, TimestampRange


def test_symbol_defaults() -> None:
    symbol = Symbol(symbol="BTCUSDT", exchange=ExchangeType.BINANCE)
    assert symbol.is_active is True
    assert symbol.created_by == "system"


def test_symbol_custom_created_by() -> None:
    symbol = Symbol(symbol="ETHUSDT", exchange=ExchangeType.BINANCE, created_by="tester")
    assert symbol.created_by == "tester"


def test_candle_requires_timezone() -> None:
    with pytest.raises(InvalidTimestampRangeError):
        Candle(
            symbol="BTCUSDT",
            interval=Interval.ONE_HOUR,
            time=datetime(2024, 1, 1),
            open=1.0,
            high=2.0,
            low=0.5,
            close=1.5,
            volume=10.0,
        )


def test_candle_valid() -> None:
    candle = Candle(
        symbol="BTCUSDT",
        interval=Interval.ONE_HOUR,
        time=datetime(2024, 1, 1, tzinfo=timezone.utc),
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=10.0,
    )
    assert candle.symbol == "BTCUSDT"


def test_fetch_job_timezone_validation() -> None:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)
    job = FetchJob(
        symbol="BTCUSDT",
        interval=Interval.ONE_DAY,
        time_range=TimestampRange(start=start, end=end),
        status="pending",
    )
    assert job.status == "pending"


def test_fetch_job_requires_timezone_range() -> None:
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)
    with pytest.raises(InvalidTimestampRangeError):
        FetchJob(
            symbol="BTCUSDT",
            interval=Interval.ONE_DAY,
            time_range=TimestampRange(start=start, end=end),
            status="pending",
        )


def test_fetch_job_job_id_mutation() -> None:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)
    job = FetchJob(
        symbol="BTCUSDT",
        interval=Interval.ONE_DAY,
        time_range=TimestampRange(start=start, end=end),
        status="pending",
    )
    job.job_id = 10
    assert job.job_id == 10
