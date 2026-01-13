import pytest
import datetime
from cryptostory.domain.models import FetchJob
from cryptostory.domain.value_objects import Interval
from cryptostory.infrastructure.database.repositories.fetch_job_repository import (
    FetchJobRepository,
)


@pytest.mark.asyncio
async def test_job_repo(db_session):
    repo = FetchJobRepository(db_session)
    job = FetchJob(
        symbol="BTCUSDT",
        interval=Interval.ONE_HOUR,
        start_time=datetime.datetime.now(datetime.timezone.utc),
        end_time=datetime.datetime.now(datetime.timezone.utc),
    )
    await repo.create(job)
    retrieved = await repo.get_by_id(job.id)
    assert retrieved.symbol == "BTCUSDT"
