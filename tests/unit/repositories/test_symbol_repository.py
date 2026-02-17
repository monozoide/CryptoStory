"""Tests for SymbolRepository."""

from datetime import datetime, timezone

import pytest

from cryptostory.domain.models import Symbol
from cryptostory.domain.value_objects import ExchangeType
from cryptostory.repositories.symbol_repository import SymbolRepository
from tests.unit.repositories.conftest import FakeResult, fake_result


@pytest.mark.asyncio
async def test_add_symbol(async_session) -> None:
    repo = SymbolRepository(async_session)
    symbol = Symbol(symbol="BTCUSDT", exchange=ExchangeType.BINANCE)
    await repo.add(symbol)
    async_session.add.assert_called_once()
    async_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_get_symbol_cache_hit(async_session) -> None:
    repo = SymbolRepository(async_session)
    symbol = Symbol(symbol="BTCUSDT", exchange=ExchangeType.BINANCE)
    await repo.add(symbol)
    fetched = await repo.get("BTCUSDT")
    assert fetched == symbol
    async_session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_get_symbol_cache_miss(async_session) -> None:
    repo = SymbolRepository(async_session)
    now = datetime.now(tz=timezone.utc)
    model = type("Model", (), {
        "symbol": "ETHUSDT",
        "exchange": ExchangeType.BINANCE,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "created_by": "system",
    })
    async_session.execute.return_value = FakeResult([model])
    fetched = await repo.get("ETHUSDT")
    assert fetched is not None
    assert fetched.symbol == "ETHUSDT"


@pytest.mark.asyncio
async def test_get_symbol_not_found(async_session) -> None:
    repo = SymbolRepository(async_session)
    async_session.execute.return_value = fake_result([])
    assert await repo.get("MISSING") is None


@pytest.mark.asyncio
async def test_list_active(async_session) -> None:
    repo = SymbolRepository(async_session)
    now = datetime.now(tz=timezone.utc)
    model = type("Model", (), {
        "symbol": "BTCUSDT",
        "exchange": ExchangeType.BINANCE,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "created_by": "system",
    })
    async_session.execute.return_value = fake_result([model])
    symbols = await repo.list_active()
    assert len(symbols) == 1


@pytest.mark.asyncio
async def test_deactivate_updates_cache(async_session) -> None:
    repo = SymbolRepository(async_session)
    symbol = Symbol(symbol="BTCUSDT", exchange=ExchangeType.BINANCE)
    await repo.add(symbol)
    await repo.deactivate("BTCUSDT")
    assert repo._cache["BTCUSDT"].is_active is False
