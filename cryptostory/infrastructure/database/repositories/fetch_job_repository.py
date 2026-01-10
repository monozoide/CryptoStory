from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from typing import Optional
from uuid import UUID
from cryptostory.domain.models import FetchJob, JobStatus
from cryptostory.infrastructure.database.schema import fetch_jobs_table


class FetchJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, job: FetchJob):
        await self.session.execute(insert(fetch_jobs_table).values(job.__dict__))

    async def get_by_id(self, job_id: UUID) -> Optional[FetchJob]:
        row = (
            await self.session.execute(
                select(fetch_jobs_table).where(fetch_jobs_table.c.id == job_id)
            )
        ).fetchone()
        return FetchJob(**row._asdict()) if row else None

    async def update_status(self, job_id: UUID, status: JobStatus):
        await self.session.execute(
            update(fetch_jobs_table)
            .where(fetch_jobs_table.c.id == job_id)
            .values(status=status)
        )
