"""Async Binance API client."""

from __future__ import annotations

from datetime import datetime

import httpx

from cryptostory.domain.value_objects import Interval


class BinanceClient:
    """HTTPX wrapper for Binance uiKlines endpoint."""

    def __init__(self, base_url: str = "https://api.binance.com", timeout: float = 30.0) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def get_klines(
        self,
        symbol: str,
        interval: Interval,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> list[list[object]]:
        """Fetch uiKlines from Binance.

        Args:
            symbol: Trading symbol.
            interval: Candle interval.
            start_time: UTC start time.
            end_time: UTC end time.
            limit: Max number of candles.

        Returns:
            Raw Binance response rows.
        """
        params = {
            "symbol": symbol,
            "interval": interval.value,
            "startTime": int(start_time.timestamp() * 1000),
            "endTime": int(end_time.timestamp() * 1000),
            "limit": limit,
        }
        response = await self._client.get("/api/v3/uiKlines", params=params)
        response.raise_for_status()
        return response.json()
