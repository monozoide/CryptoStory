"""Base repository with shared behavior."""

from __future__ import annotations

import asyncio
import logging
from typing import Callable, Coroutine, TypeVar

from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository:
    """Provide shared repository helpers."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        """Return the underlying SQLAlchemy async session."""
        return self._session

    async def _retry_on_deadlock(self, func: Callable[[], Coroutine[object, object, T]], retries: int = 3) -> T:
        """Retry a coroutine if a deadlock is detected.

        Args:
            func: Coroutine factory.
            retries: Number of retries.

        Returns:
            Result of the coroutine.

        Raises:
            DBAPIError: If retries are exhausted or error is not a deadlock.
        """
        for attempt in range(retries + 1):
            try:
                return await func()
            except DBAPIError as exc:
                if not self._is_deadlock(exc) or attempt == retries:
                    raise
                delay = 0.2 * (attempt + 1)
                logger.warning("Deadlock detected, retrying in %.1fs", delay)
                await asyncio.sleep(delay)
        raise RuntimeError("Unreachable")

    @staticmethod
    def _is_deadlock(exc: DBAPIError) -> bool:
        if exc.orig is None:
            return False
        sqlstate = getattr(exc.orig, "pgcode", None)
        return sqlstate == "40P01"
