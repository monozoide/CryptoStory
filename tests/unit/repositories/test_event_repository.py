"""Tests for EventRepository."""

import pytest

from cryptostory.repositories.event_repository import EventRepository
from tests.unit.repositories.conftest import fake_result


@pytest.mark.asyncio
async def test_add_event(async_session) -> None:
    repo = EventRepository(async_session)
    await repo.add(symbol="BTCUSDT", event_type="test", payload="payload")
    async_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_list_for_symbol(async_session) -> None:
    repo = EventRepository(async_session)
    model = type("Model", (), {"symbol": "BTCUSDT"})
    async_session.execute.return_value = fake_result([model])
    events = await repo.list_for_symbol("BTCUSDT")
    assert len(events) == 1
