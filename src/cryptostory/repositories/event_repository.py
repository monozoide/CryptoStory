"""Repository for audit events."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cryptostory.infrastructure.schemas import EventModel
from .base_repository import BaseRepository


class EventRepository(BaseRepository):
    """Manage audit events."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def add(self, symbol: str | None, event_type: str, payload: str, created_by: str = "system") -> None:
        """Insert a new audit event."""
        model = EventModel(symbol=symbol, event_type=event_type, payload=payload, created_by=created_by)
        self.session.add(model)
        await self.session.flush()

    async def list_for_symbol(self, symbol: str) -> list[EventModel]:
        """Return all events for a symbol."""
        result = await self.session.execute(select(EventModel).where(EventModel.symbol == symbol))
        return list(result.scalars().all())
