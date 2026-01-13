import pytest
from cryptostory.domain.value_objects import Interval
from cryptostory.infrastructure.database.repositories.configured_symbol_repository import (
    ConfiguredSymbolRepository,
)


@pytest.mark.asyncio
async def test_config_repo(db_session):
    repo = ConfiguredSymbolRepository(db_session)
    await repo.add("BTCUSDT", Interval.ONE_HOUR)
    symbols = await repo.list_all()
    assert len(symbols) == 1
