from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

@dataclass
class ImportLog:
    """Domain model for ImportLog (corresponds to importlogs table)"""
    importid: UUID
    symbol: str
    quote: str
    interval: str
    exchange: str
    starttime: Optional[int] = None  # Unix timestamp ms
    endtime: Optional[int] = None    # Unix timestamp ms
    limitparam: int = 1000
    executionstart: datetime = None
    executionend: Optional[datetime] = None
    durationseconds: Optional[float] = None
    recordsrequested: Optional[int] = None
    recordsreceived: int = 0
    recordsinserted: int = 0
    recordsupdated: int = 0
    recordsfailed: int = 0
    status: str = "SUCCESS"  # SUCCESS, PARTIAL, FAILURE
    checksumsha256: Optional[str] = None
    validationpassed: bool = False
    errorcount: int = 0
    errormessage: Optional[str] = None
    errorcode: Optional[int] = None
    ratelimitused: int = 0
    ratelimitafter: int = 0
    userwhotriggered: Optional[str] = None
    triggeredby: str = "MANUAL"  # MANUAL, SCHEDULER, RETRY
    createdat: Optional[datetime] = None
    updatedat: Optional[datetime] = None

    @classmethod
    def create(cls, symbol: str, quote: str, interval: str, triggered_by: str = "MANUAL"):
        """Factory method"""
        from datetime import timezone
        now = datetime.now(timezone.utc)

        return cls(
            importid=uuid4(),
            symbol=symbol,
            quote=quote,
            interval=interval,
            exchange="BINANCE",
            executionstart=now,
            triggeredby=triggered_by,
            status="SUCCESS",
            createdat=now,
            updatedat=now
        )
