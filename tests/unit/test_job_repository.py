import pytest
from uuid import uuid4
from datetime import datetime, timezone
from cryptostory.backend.domain.models.fetchjob import FetchJob
from cryptostory.backend.dal.repositories.jobrepository import JobRepository

@pytest.mark.asyncio
async def test_create_fetchjob(test_db):
    """Test création d'un FetchJob"""
    repo = JobRepository(test_db)

    job = FetchJob(
        executionid=uuid4(),
        taskname="BTCUSDT_1h_fetch",
        symbol="BTCUSDT",
        interval="1h",
        scheduledat=datetime.now(timezone.utc),  # ✅ Correct
        status="PENDING",
        createdat=datetime.now(timezone.utc)
    )

    created = await repo.create(job)
    assert created.executionid == job.executionid
    assert created.symbol == "BTCUSDT"
    assert created.status == "PENDING"

@pytest.mark.asyncio
async def test_get_fetchjob(test_db):
    """Test récupération d'un FetchJob"""
    repo = JobRepository(test_db)

    # Create
    job = FetchJob.create(symbol="ETHUSDT", interval="4h")
    await repo.create(job)

    # Get
    retrieved = await repo.get(job.executionid)
    assert retrieved is not None
    assert retrieved.symbol == "ETHUSDT"
    assert retrieved.interval == "4h"

@pytest.mark.asyncio
async def test_list_pending_jobs(test_db):
    """Test listage des jobs pending"""
    repo = JobRepository(test_db)

    # Create multiple jobs
    job1 = FetchJob.create(symbol="BTCUSDT", interval="1h")
    job2 = FetchJob.create(symbol="ETHUSDT", interval="1h")

    await repo.create(job1)
    await repo.create(job2)

    # List pending
    pending = await repo.list_pending()
    assert len(pending) >= 2
    assert all(j.status == "PENDING" for j in pending)
