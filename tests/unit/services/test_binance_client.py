"""Tests for BinanceClient."""

from datetime import datetime, timezone

import pytest

from cryptostory.domain.value_objects import Interval
from cryptostory.services.binance_client import BinanceClient


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


@pytest.mark.asyncio
async def test_get_klines(monkeypatch) -> None:
    payload = [[1704067200000, "1", "2", "0.5", "1.5", "10"]]

    async def fake_get(self, url, params=None):
        return FakeResponse(payload)

    monkeypatch.setattr("httpx.AsyncClient.get", fake_get)
    client = BinanceClient(base_url="https://example.com")
    rows = await client.get_klines(
        "BTCUSDT",
        Interval.ONE_MINUTE,
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    assert rows == payload
    await client.close()
