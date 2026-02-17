"""Value objects for the CryptoStory domain."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable

from .exceptions import InvalidIntervalError, InvalidTimestampRangeError


class Interval(str, Enum):
    """Supported Binance candle intervals."""

    ONE_MINUTE = "1m"
    FIVE_MINUTE = "5m"
    FIFTEEN_MINUTE = "15m"
    ONE_HOUR = "1h"
    FOUR_HOUR = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"

    @classmethod
    def from_value(cls, value: str) -> "Interval":
        """Parse an interval from its string representation.

        Args:
            value: Interval string from Binance.

        Returns:
            Parsed Interval.

        Raises:
            InvalidIntervalError: If the interval is not supported.
        """
        try:
            return cls(value)
        except ValueError as exc:
            raise InvalidIntervalError(f"Unsupported interval: {value}") from exc


class ExchangeType(str, Enum):
    """Supported exchange types."""

    BINANCE = "binance"


@dataclass(frozen=True)
class TimestampRange:
    """Time range value object in UTC."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise InvalidTimestampRangeError("TimestampRange requires timezone-aware datetimes.")
        if self.start > self.end:
            raise InvalidTimestampRangeError("TimestampRange start must be before end.")

    def duration_seconds(self) -> int:
        """Return duration in seconds."""
        return int((self.end - self.start).total_seconds())


@dataclass(frozen=True)
class CandleOHLCV:
    """Immutable OHLCV data point."""

    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        if self.open_time.tzinfo is None:
            raise InvalidTimestampRangeError("Candle open_time must be timezone-aware.")
        if any(value < 0 for value in self._numeric_values()):
            raise ValueError("OHLCV values must be non-negative.")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("High must be >= open, close, and low.")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("Low must be <= open, close, and high.")

    def _numeric_values(self) -> Iterable[float]:
        return (self.open, self.high, self.low, self.close, self.volume)

    @classmethod
    def from_binance(cls, payload: list[str | float | int]) -> "CandleOHLCV":
        """Create CandleOHLCV from Binance api response row.

        Args:
            payload: Row containing [open_time, open, high, low, close, volume, ...].

        Returns:
            CandleOHLCV instance.
        """
        open_time_ms = int(payload[0])
        open_time = datetime.fromtimestamp(open_time_ms / 1000, tz=timezone.utc)
        return cls(
            open_time=open_time,
            open=float(payload[1]),
            high=float(payload[2]),
            low=float(payload[3]),
            close=float(payload[4]),
            volume=float(payload[5]),
        )
