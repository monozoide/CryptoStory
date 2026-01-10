import datetime
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional
from .value_objects import Interval


@dataclass
class Candle:
    symbol: str
    interval: Interval
    open_time: datetime.datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: datetime.datetime
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float


@dataclass
class ConfiguredSymbol:
    symbol: str
    interval: Interval
    is_active: bool = True
    id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"


@dataclass
class FetchJob:
    symbol: str
    interval: Interval
    start_time: datetime.datetime
    end_time: datetime.datetime
    id: UUID = field(default_factory=uuid4)
    status: JobStatus = JobStatus.PENDING
    logs: list[str] = field(default_factory=list)
    created_at: Optional[datetime.datetime] = None
