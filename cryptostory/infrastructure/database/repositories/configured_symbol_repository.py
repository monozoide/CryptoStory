from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from typing import List
from cryptostory.domain.models import ConfiguredSymbol
from cryptostory.domain.value_objects import Interval
from cryptostory.infrastructure.database.schema import configured_symbols_table


class ConfiguredSymbolRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, symbol: str, interval: Interval):
        await self.session.execute(
            insert(configured_symbols_table).values(symbol=symbol, interval=interval)
        )

    async def list_active(self) -> List[ConfiguredSymbol]:
        return [
            ConfiguredSymbol(**row._asdict())
            for row in (
                await self.session.execute(
                    select(configured_symbols_table).where(
                        configured_symbols_table.c.is_active is True
                    )
                )
            ).fetchall()
        ]

    async def list_all(self) -> List[ConfiguredSymbol]:
        return [
            ConfiguredSymbol(**row._asdict())
            for row in (
                await self.session.execute(select(configured_symbols_table))
            ).fetchall()
        ]
