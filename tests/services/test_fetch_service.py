import pytest
from unittest.mock import AsyncMock
from cryptostory.services.fetch_service import FetchService
from cryptostory.domain.models import ConfiguredSymbol
from cryptostory.domain.value_objects import Interval


@pytest.mark.asyncio
async def test_fetch_service():
    client = AsyncMock()
    repo = AsyncMock()
    limiter = AsyncMock()
    service = FetchService(client, repo, limiter)
    await service.fetch_and_store(
        ConfiguredSymbol(symbol="BTCUSDT", interval=Interval.ONE_HOUR)
    )
    client.get_ui_klines.assert_called_once()
    repo.bulk_upsert.assert_called_once()
