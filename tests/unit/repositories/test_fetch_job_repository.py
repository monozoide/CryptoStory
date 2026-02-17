"""Tests for FetchJobRepository."""

from datetime import datetime, timezone

import pytest

from cryptostory.domain.models import FetchJob
from cryptostory.domain.value_objects import Interval, TimestampRange
from cryptostory.repositories.fetch_job_repository import FetchJobRepository
from tests.unit.repositories.conftest import fake_result


@pytest.mark.asyncio
async def test_create_fetch_job(async_session) -> None:
    repo = FetchJobRepository(async_session)
    time_range = TimestampRange(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        end=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    job = FetchJob(symbol="BTCUSDT", interval=Interval.ONE_DAY, time_range=time_range, status="pending")
    await repo.create(job)
    async_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_get_fetch_job(async_session) -> None:
    repo = FetchJobRepository(async_session)
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    model = type("Model", (), {
        "id": 1,
        "symbol": "BTCUSDT",
        "interval": Interval.ONE_DAY,
        "start_time": now,
        "end_time": now,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
        "created_by": "system",
    })
    async_session.execute.return_value = fake_result([model])
    job = await repo.get(1)
    assert job is not None
    assert job.job_id == 1


@pytest.mark.asyncio
async def test_update_status(async_session) -> None:
    repo = FetchJobRepository(async_session)
    await repo.update_status(1, "done")
    async_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_list_pending(async_session) -> None:
    repo = FetchJobRepository(async_session)
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    model = type("Model", (), {
        "id": 1,
        "symbol": "BTCUSDT",
        "interval": Interval.ONE_DAY,
        "start_time": now,
        "end_time": now,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
        "created_by": "system",
    })
    async_session.execute.return_value = fake_result([model])
    jobs = await repo.list_pending()
    assert len(jobs) == 1
