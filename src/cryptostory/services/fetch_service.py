"""Fetch service orchestrating Binance data ingestion."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Sequence

import httpx

from cryptostory.domain.exceptions import CandleMismatchError, DomainException
from cryptostory.domain.models import Candle
from cryptostory.domain.value_objects import CandleOHLCV, Interval
from cryptostory.repositories.candle_repository import CandleRepository
from cryptostory.repositories.event_repository import EventRepository
from .binance_client import BinanceClient
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class FetchService:
    """Coordinate Binance fetch with persistence."""

    def __init__(
        self,
        client: BinanceClient,
        rate_limiter: RateLimiter,
        candle_repository: CandleRepository,
        event_repository: EventRepository,
    ) -> None:
        self._client = client
        self._rate_limiter = rate_limiter
        self._candle_repository = candle_repository
        self._event_repository = event_repository

    async def fetch_and_store(
        self,
        symbol: str,
        interval: Interval,
        start_time: datetime,
        end_time: datetime,
    ) -> int:
        """Fetch candles from Binance and store them.

        Returns:
            Number of candles inserted.
        """
        await self._rate_limiter.acquire(tokens=1)
        rows = await self._fetch_with_retry(symbol, interval, start_time, end_time)
        candles = self._rows_to_candles(symbol, interval, rows)
        deduped = await self._deduplicate(symbol, interval, candles)
        inserted = await self._candle_repository.bulk_insert(deduped)
        return inserted

    async def _fetch_with_retry(
        self,
        symbol: str,
        interval: Interval,
        start_time: datetime,
        end_time: datetime,
        retries: int = 3,
    ) -> list[list[object]]:
        for attempt in range(retries + 1):
            try:
                return await self._client.get_klines(symbol, interval, start_time, end_time)
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status == 429 and attempt < retries:
                    await self._backoff(attempt)
                    continue
                if status >= 500 and attempt < retries:
                    await self._backoff(attempt)
                    continue
                raise DomainException(f"Binance error {status}") from exc
            except httpx.TimeoutException as exc:
                if attempt < retries:
                    await self._backoff(attempt)
                    continue
                raise DomainException("Binance timeout") from exc
        raise DomainException("Retry exhaustion")

    async def _backoff(self, attempt: int) -> None:
        delay = (2**attempt) + 0.1
        await asyncio.sleep(delay)

    def _rows_to_candles(
        self, symbol: str, interval: Interval, rows: Sequence[Sequence[object]]
    ) -> list[Candle]:
        candles: list[Candle] = []
        for row in rows:
            ohlcv = CandleOHLCV.from_binance(list(row))
            candles.append(
                Candle(
                    symbol=symbol,
                    interval=interval,
                    time=ohlcv.open_time,
                    open=ohlcv.open,
                    high=ohlcv.high,
                    low=ohlcv.low,
                    close=ohlcv.close,
                    volume=ohlcv.volume,
                    created_at=datetime.now(tz=timezone.utc),
                    updated_at=datetime.now(tz=timezone.utc),
                    created_by="binance",
                )
            )
        return candles

    async def _deduplicate(self, symbol: str, interval: Interval, candles: list[Candle]) -> list[Candle]:
        times = [candle.time for candle in candles]
        existing = await self._candle_repository.fetch_existing_times(symbol, interval, times)
        deduped: list[Candle] = []
        for candle in candles:
            stored = existing.get(candle.time)
            if stored is None:
                deduped.append(candle)
                continue
            if stored.close != candle.close:
                await self._event_repository.add(
                    symbol=symbol,
                    event_type="candle_mismatch",
                    payload=f"{candle.time.isoformat()} close {stored.close} -> {candle.close}",
                )
                logger.warning("Candle mismatch detected for %s %s", symbol, candle.time)
                raise CandleMismatchError("Conflicting candle close price detected")
        return deduped
