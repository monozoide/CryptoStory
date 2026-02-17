"""Tests for value objects."""

from datetime import datetime, timezone

import pytest

from cryptostory.domain.exceptions import InvalidIntervalError, InvalidTimestampRangeError
from cryptostory.domain.value_objects import CandleOHLCV, ExchangeType, Interval, TimestampRange


def test_interval_from_value_valid() -> None:
    assert Interval.from_value("1m") == Interval.ONE_MINUTE


def test_interval_from_value_invalid() -> None:
    with pytest.raises(InvalidIntervalError):
        Interval.from_value("2m")


def test_exchange_type_enum() -> None:
    assert ExchangeType.BINANCE.value == "binance"


def test_timestamp_range_valid() -> None:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)
    range_obj = TimestampRange(start=start, end=end)
    assert range_obj.duration_seconds() == 86400


def test_timestamp_range_invalid_timezone() -> None:
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)
    with pytest.raises(InvalidTimestampRangeError):
        TimestampRange(start=start, end=end)


def test_timestamp_range_invalid_order() -> None:
    start = datetime(2024, 1, 2, tzinfo=timezone.utc)
    end = datetime(2024, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(InvalidTimestampRangeError):
        TimestampRange(start=start, end=end)


def test_candle_ohlcv_from_binance() -> None:
    payload = [
        1704067200000,
        "100.0",
        "110.0",
        "90.0",
        "105.0",
        "123.0",
    ]
    candle = CandleOHLCV.from_binance(payload)
    assert candle.open == 100.0
    assert candle.high == 110.0
    assert candle.low == 90.0
    assert candle.close == 105.0
    assert candle.volume == 123.0


def test_candle_ohlcv_negative_value() -> None:
    payload = [
        1704067200000,
        "-1.0",
        "1.0",
        "0.5",
        "0.8",
        "10.0",
    ]
    with pytest.raises(ValueError):
        CandleOHLCV.from_binance(payload)


def test_candle_ohlcv_invalid_high() -> None:
    payload = [
        1704067200000,
        "10.0",
        "9.0",
        "8.0",
        "9.5",
        "1.0",
    ]
    with pytest.raises(ValueError):
        CandleOHLCV.from_binance(payload)


def test_candle_ohlcv_invalid_low() -> None:
    payload = [
        1704067200000,
        "10.0",
        "12.0",
        "11.0",
        "9.0",
        "1.0",
    ]
    with pytest.raises(ValueError):
        CandleOHLCV.from_binance(payload)
