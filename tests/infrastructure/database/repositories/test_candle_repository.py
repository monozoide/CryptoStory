import pytest
import datetime
from cryptostory.domain.models import Candle
from cryptostory.domain.value_objects import Interval
from cryptostory.infrastructure.database.repositories.candle_repository import (
    CandleRepository,
)


@pytest.mark.asyncio
async def test_candle_repo(db_session):
    repo = CandleRepository(db_session)
    candle = Candle(
        symbol="BTCUSDT",
        interval=Interval.ONE_HOUR,
        open_time=datetime.datetime.now(datetime.timezone.utc),
        open=1,
        high=2,
        low=0,
        close=1.5,
        volume=100,
        close_time=datetime.datetime.now(datetime.timezone.utc),
        quote_asset_volume=100,
        number_of_trades=1,
        taker_buy_base_asset_volume=1,
        taker_buy_quote_asset_volume=1,
    )
    await repo.bulk_upsert([candle])
    retrieved = await repo.get_last_candle("BTCUSDT", Interval.ONE_HOUR.value)
    assert retrieved.symbol == "BTCUSDT"
