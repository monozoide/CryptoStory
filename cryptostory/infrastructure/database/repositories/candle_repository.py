from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from typing import List, Optional
from cryptostory.domain.models import Candle
from cryptostory.infrastructure.database.schema import candles_table


class CandleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_upsert(self, candles: List[Candle]):
        if not candles:
            return
        stmt = insert(candles_table).values([c.__dict__ for c in candles])
        update_cols = {
            c.name: getattr(stmt.excluded, c.name)
            for c in candles_table.c
            if not c.primary_key
        }
        await self.session.execute(
            stmt.on_conflict_do_update(
                index_elements=["symbol", "interval", "open_time"], set_=update_cols
            )
        )

    async def get_last_candle(self, symbol: str, interval: str) -> Optional[Candle]:
        stmt = (
            select(candles_table)
            .where(
                candles_table.c.symbol == symbol, candles_table.c.interval == interval
            )
            .order_by(candles_table.c.open_time.desc())
            .limit(1)
        )
        row = (await self.session.execute(stmt)).fetchone()
        return Candle(**row._asdict()) if row else None
