# tests/conftest.py
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import text

from cryptostory.infrastructure.database.session import get_database_url
from cryptostory.infrastructure.database.schema import metadata


@pytest_asyncio.fixture(scope="session", autouse=True)
async def test_db():
    """Create and tear down a test database."""
    test_db_url = get_database_url(testing=True)
    sync_test_db_url = test_db_url.replace("asyncpg", "psycopg2")

    if database_exists(sync_test_db_url):
        drop_database(sync_test_db_url)
    create_database(sync_test_db_url)

    engine = create_async_engine(test_db_url)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
        await conn.execute(
            text(
                "SELECT create_hypertable('candles', 'open_time', if_not_exists => TRUE);"
            )
        )

    yield

    drop_database(sync_test_db_url)


@pytest_asyncio.fixture(scope="function")
async def db_session(test_db) -> AsyncSession:
    """Provides a transactional session for each test function."""
    test_db_url = get_database_url(testing=True)
    engine = create_async_engine(test_db_url)
    connection = await engine.connect()
    trans = await connection.begin()

    TestingSessionLocal = sessionmaker(
        bind=connection, class_=AsyncSession, expire_on_commit=False
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()
        await engine.dispose()
