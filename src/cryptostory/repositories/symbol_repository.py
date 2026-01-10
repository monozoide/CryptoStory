"""Repository for Symbol entities."""

from __future__ import annotations

from typing import Dict, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cryptostory.domain.models import Symbol
from cryptostory.domain.value_objects import ExchangeType
from cryptostory.infrastructure.schemas import SymbolModel
from .base_repository import BaseRepository


class SymbolRepository(BaseRepository):
    """Manage symbol persistence with caching."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._cache: Dict[str, Symbol] = {}

    async def add(self, symbol: Symbol) -> Symbol:
        """Persist a symbol and cache it."""
        model = SymbolModel(
            symbol=symbol.symbol,
            exchange=symbol.exchange,
            is_active=symbol.is_active,
            created_at=symbol.created_at,
            updated_at=symbol.updated_at,
            created_by=symbol.created_by,
        )
        self.session.add(model)
        await self.session.flush()
        self._cache[symbol.symbol] = symbol
        return symbol

    async def get(self, symbol_code: str) -> Optional[Symbol]:
        """Get a symbol by its code."""
        if symbol_code in self._cache:
            return self._cache[symbol_code]
        result = await self.session.execute(select(SymbolModel).where(SymbolModel.symbol == symbol_code))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        symbol = Symbol(
            symbol=model.symbol,
            exchange=ExchangeType(model.exchange),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
        )
        self._cache[symbol_code] = symbol
        return symbol

    async def list_active(self) -> list[Symbol]:
        """List active symbols."""
        result = await self.session.execute(select(SymbolModel).where(SymbolModel.is_active.is_(True)))
        symbols: list[Symbol] = []
        for model in result.scalars().all():
            symbols.append(
                Symbol(
                    symbol=model.symbol,
                    exchange=ExchangeType(model.exchange),
                    is_active=model.is_active,
                    created_at=model.created_at,
                    updated_at=model.updated_at,
                    created_by=model.created_by,
                )
            )
        return symbols

    async def deactivate(self, symbol_code: str) -> None:
        """Soft-delete a symbol by deactivating it."""
        await self.session.execute(
            update(SymbolModel).where(SymbolModel.symbol == symbol_code).values(is_active=False)
        )
        if symbol_code in self._cache:
            cached = self._cache[symbol_code]
            self._cache[symbol_code] = Symbol(
                symbol=cached.symbol,
                exchange=cached.exchange,
                is_active=False,
                created_at=cached.created_at,
                updated_at=cached.updated_at,
                created_by=cached.created_by,
            )

    def clear_cache(self) -> None:
        """Clear cached symbols."""
        self._cache.clear()
