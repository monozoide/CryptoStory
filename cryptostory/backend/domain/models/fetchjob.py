from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

@dataclass
class FetchJob:
    """
    Domain model for FetchJob (corresponds to taskexecutions table).
    Represents a scheduled or executed fetch task.
    """
    executionid: UUID
    taskname: str
    symbol: str
    interval: str
    scheduledat: datetime  # ⚠️ PAS start_time !
    startedat: Optional[datetime] = None
    completedat: Optional[datetime] = None
    durationseconds: Optional[float] = None
    status: str = "PENDING"  # PENDING, RUNNING, SUCCESS, FAILURE, TIMEOUT
    exitcode: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    importid: Optional[UUID] = None
    createdat: Optional[datetime] = None

    @classmethod
    def create(cls, symbol: str, interval: str, taskname: str = None):
        """Factory method to create a new FetchJob"""
        from datetime import timezone

        if taskname is None:
            taskname = f"{symbol}_{interval}_fetch"

        return cls(
            executionid=uuid4(),
            taskname=taskname,
            symbol=symbol,
            interval=interval,
            scheduledat=datetime.now(timezone.utc),
            status="PENDING",
            createdat=datetime.now(timezone.utc)
        )

    def mark_started(self):
        """Mark job as started"""
        from datetime import timezone
        self.status = "RUNNING"
        self.startedat = datetime.now(timezone.utc)

    def mark_completed(self, success: bool = True, exit_code: int = 0):
        """Mark job as completed"""
        from datetime import timezone
        self.status = "SUCCESS" if success else "FAILURE"
        self.completedat = datetime.now(timezone.utc)
        self.exitcode = exit_code
        if self.startedat:
            self.durationseconds = (self.completedat - self.startedat).total_seconds()
