"""Domain entities for CryptoStory."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .exceptions import InvalidTimestampRangeError
from .value_objects import ExchangeType, Interval, TimestampRange


@dataclass
class Symbol:
    """Trading symbol tracked in the system."""

    symbol: str
    exchange: ExchangeType
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    created_by: str = "system"


@dataclass
class Candle:
    """OHLCV candle entity."""

    symbol: str
    interval: Interval
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    created_by: str = "system"

    def __post_init__(self) -> None:
        if self.time.tzinfo is None:
            raise InvalidTimestampRangeError("Candle time must be timezone-aware.")


@dataclass
class FetchJob:
    """Represents a fetch job for a symbol and interval."""

    symbol: str
    interval: Interval
    time_range: TimestampRange
    status: str
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    created_by: str = "system"
    job_id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.time_range.start.tzinfo is None or self.time_range.end.tzinfo is None:
            raise InvalidTimestampRangeError("FetchJob time range must be timezone-aware.")


@dataclass(frozen=True)
class TimestampRangeEntity:
    """Compatibility entity wrapper for TimestampRange if needed."""

    start: datetime
    end: datetime

    def to_value_object(self) -> TimestampRange:
        """Convert to TimestampRange value object."""
        return TimestampRange(start=self.start, end=self.end)
