"""Service test fixtures."""

from unittest.mock import AsyncMock

import pytest

from cryptostory.services.binance_client import BinanceClient


@pytest.fixture()
def mock_binance_client() -> AsyncMock:
    return AsyncMock(spec=BinanceClient)
