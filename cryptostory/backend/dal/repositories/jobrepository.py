from typing import List, Optional
from uuid import UUID
from datetime import datetime
from cryptostory.backend.domain.models.fetchjob import FetchJob

class JobRepository:
    """Repository for FetchJob (taskexecutions table)"""

    def __init__(self, db_connection):
        self.conn = db_connection

    async def create(self, job: FetchJob) -> FetchJob:
        """Create a new FetchJob"""
        query = """
            INSERT INTO taskexecutions (
                executionid, taskname, symbol, interval, scheduledat,
                startedat, completedat, durationseconds, status,
                exitcode, stdout, stderr, importid, createdat
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        await self.conn.execute(
            query,
            (
                str(job.executionid),
                job.taskname,
                job.symbol,
                job.interval,
                job.scheduledat.isoformat(),
                job.startedat.isoformat() if job.startedat else None,
                job.completedat.isoformat() if job.completedat else None,
                job.durationseconds,
                job.status,
                job.exitcode,
                job.stdout,
                job.stderr,
                str(job.importid) if job.importid else None,
                job.createdat.isoformat() if job.createdat else datetime.now().isoformat()
            )
        )
        await self.conn.commit()
        return job

    async def get(self, execution_id: UUID) -> Optional[FetchJob]:
        """Get a FetchJob by ID"""
        cursor = await self.conn.execute(
            "SELECT * FROM taskexecutions WHERE executionid = ?",
            (str(execution_id),)
        )
        row = await cursor.fetchone()

        if not row:
            return None

        return self._row_to_model(row)

    async def list_pending(self) -> List[FetchJob]:
        """List all pending jobs"""
        cursor = await self.conn.execute(
            "SELECT * FROM taskexecutions WHERE status = 'PENDING' ORDER BY scheduledat ASC"
        )
        rows = await cursor.fetchall()
        return [self._row_to_model(row) for row in rows]

    async def update(self, job: FetchJob) -> FetchJob:
        """Update a FetchJob"""
        query = """
            UPDATE taskexecutions SET
                taskname = ?,
                symbol = ?,
                interval = ?,
                scheduledat = ?,
                startedat = ?,
                completedat = ?,
                durationseconds = ?,
                status = ?,
                exitcode = ?,
                stdout = ?,
                stderr = ?,
                importid = ?
            WHERE executionid = ?
        """

        await self.conn.execute(
            query,
            (
                job.taskname,
                job.symbol,
                job.interval,
                job.scheduledat.isoformat(),
                job.startedat.isoformat() if job.startedat else None,
                job.completedat.isoformat() if job.completedat else None,
                job.durationseconds,
                job.status,
                job.exitcode,
                job.stdout,
                job.stderr,
                str(job.importid) if job.importid else None,
                str(job.executionid)
            )
        )
        await self.conn.commit()
        return job

    def _row_to_model(self, row) -> FetchJob:
        """Convert database row to FetchJob model"""
        return FetchJob(
            executionid=UUID(row[0]),
            taskname=row[1],
            symbol=row[2],
            interval=row[3],
            scheduledat=datetime.fromisoformat(row[4]),
            startedat=datetime.fromisoformat(row[5]) if row[5] else None,
            completedat=datetime.fromisoformat(row[6]) if row[6] else None,
            durationseconds=row[7],
            status=row[8],
            exitcode=row[9],
            stdout=row[10],
            stderr=row[11],
            importid=UUID(row[12]) if row[12] else None,
            createdat=datetime.fromisoformat(row[13]) if row[13] else None
        )
