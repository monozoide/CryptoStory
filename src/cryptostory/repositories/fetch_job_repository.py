"""Repository for fetch jobs."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cryptostory.domain.models import FetchJob
from cryptostory.domain.value_objects import Interval, TimestampRange
from cryptostory.infrastructure.schemas import FetchJobModel
from .base_repository import BaseRepository


class FetchJobRepository(BaseRepository):
    """Manage fetch job persistence."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, job: FetchJob) -> FetchJob:
        """Create a fetch job."""
        model = FetchJobModel(
            symbol=job.symbol,
            interval=job.interval,
            start_time=job.time_range.start,
            end_time=job.time_range.end,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            created_by=job.created_by,
        )
        self.session.add(model)
        await self.session.flush()
        job.job_id = model.id
        return job

    async def get(self, job_id: int) -> Optional[FetchJob]:
        """Get a fetch job by id."""
        result = await self.session.execute(select(FetchJobModel).where(FetchJobModel.id == job_id))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return FetchJob(
            symbol=model.symbol,
            interval=Interval(model.interval),
            time_range=TimestampRange(start=model.start_time, end=model.end_time),
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            job_id=model.id,
        )

    async def update_status(self, job_id: int, status: str) -> None:
        """Update job status."""
        await self.session.execute(
            update(FetchJobModel).where(FetchJobModel.id == job_id).values(status=status)
        )

    async def list_pending(self) -> list[FetchJob]:
        """List pending jobs."""
        result = await self.session.execute(select(FetchJobModel).where(FetchJobModel.status == "pending"))
        jobs: list[FetchJob] = []
        for model in result.scalars().all():
            jobs.append(
                FetchJob(
                    symbol=model.symbol,
                    interval=Interval(model.interval),
                    time_range=TimestampRange(start=model.start_time, end=model.end_time),
                    status=model.status,
                    created_at=model.created_at,
                    updated_at=model.updated_at,
                    created_by=model.created_by,
                    job_id=model.id,
                )
            )
        return jobs
