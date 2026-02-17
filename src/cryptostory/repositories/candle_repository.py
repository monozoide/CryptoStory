"""Repository for candle persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from cryptostory.domain.models import Candle
from cryptostory.domain.value_objects import Interval
from cryptostory.infrastructure.schemas import CandleModel
from .base_repository import BaseRepository


class CandleRepository(BaseRepository):
    """Manage candle persistence and queries."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def bulk_insert(self, candles: Sequence[Candle]) -> int:
        """Insert candles in bulk.

        Returns:
            Number of rows inserted.
        """
        if not candles:
            return 0

        payload = [
            {
                "symbol": candle.symbol,
                "interval": candle.interval,
                "time": candle.time,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                "created_at": candle.created_at,
                "updated_at": candle.updated_at,
                "created_by": candle.created_by,
            }
            for candle in candles
        ]

        stmt = insert(CandleModel).values(payload)
        stmt = stmt.on_conflict_do_nothing(constraint="uq_candles_symbol_interval_time")
        result = await self.session.execute(stmt)
        return int(result.rowcount or 0)

    async def fetch_range(
        self, symbol: str, interval: Interval, start: datetime, end: datetime
    ) -> list[Candle]:
        """Fetch candles for a symbol and interval within a range."""
        result = await self.session.execute(
            select(CandleModel).where(
                CandleModel.symbol == symbol,
                CandleModel.interval == interval,
                CandleModel.time >= start,
                CandleModel.time <= end,
            )
        )
        candles: list[Candle] = []
        for model in result.scalars().all():
            candles.append(
                Candle(
                    symbol=model.symbol,
                    interval=Interval(model.interval),
                    time=model.time,
                    open=model.open,
                    high=model.high,
                    low=model.low,
                    close=model.close,
                    volume=model.volume,
                    created_at=model.created_at,
                    updated_at=model.updated_at,
                    created_by=model.created_by,
                )
            )
        return candles

    async def fetch_existing_times(
        self, symbol: str, interval: Interval, times: Iterable[datetime]
    ) -> dict[datetime, Candle]:
        """Fetch existing candles matching times."""
        time_list = list(times)
        if not time_list:
            return {}
        result = await self.session.execute(
            select(CandleModel).where(
                CandleModel.symbol == symbol,
                CandleModel.interval == interval,
                CandleModel.time.in_(time_list),
            )
        )
        existing: dict[datetime, Candle] = {}
        for model in result.scalars().all():
            existing[model.time] = Candle(
                symbol=model.symbol,
                interval=Interval(model.interval),
                time=model.time,
                open=model.open,
                high=model.high,
                low=model.low,
                close=model.close,
                volume=model.volume,
                created_at=model.created_at,
                updated_at=model.updated_at,
                created_by=model.created_by,
            )
        return existing
