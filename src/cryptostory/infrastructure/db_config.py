"""Database configuration and session factory."""

from __future__ import annotations

import os
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def get_engine() -> AsyncEngine:
    """Create an async SQLAlchemy engine using environment configuration."""
    database_url = os.environ.get("CRYPTOSTORY_DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/cryptostory")
    return create_async_engine(
        database_url,
        pool_size=int(os.environ.get("CRYPTOSTORY_DB_POOL_SIZE", "5")),
        max_overflow=int(os.environ.get("CRYPTOSTORY_DB_POOL_OVERFLOW", "10")),
        pool_pre_ping=True,
    )


async_session_factory = async_sessionmaker(bind=get_engine(), expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async session for use with async context managers."""
    async with async_session_factory() as session:
        yield session
