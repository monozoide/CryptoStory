import pytest
import sqlite3
import aiosqlite
from pathlib import Path

@pytest.fixture
async def test_db():
    """
    Setup in-memory SQLite database with all required tables.
    """
    conn = await aiosqlite.connect(":memory:")

    # Lire et exécuter le script de migration
    migration_file = Path(__file__).parent.parent / "cryptostory" / "backend" / "dal" / "migrations" / "001_initial_schema.sql"

    if migration_file.exists():
        with open(migration_file, 'r') as f:
            schema_sql = f.read()
        await conn.executescript(schema_sql)
    else:
        # Fallback: créer les tables manuellement
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS configured_symbols (
                symbolid TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                quote TEXT NOT NULL,
                interval TEXT NOT NULL,
                exchange TEXT NOT NULL DEFAULT 'BINANCE',
                isactive INTEGER DEFAULT 1,
                createdat TEXT DEFAULT CURRENT_TIMESTAMP,
                updatedat TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exchange, symbol, quote, interval)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS taskexecutions (
                executionid TEXT PRIMARY KEY,
                taskname TEXT NOT NULL,
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                scheduledat TEXT NOT NULL,
                startedat TEXT,
                completedat TEXT,
                durationseconds REAL,
                status TEXT NOT NULL CHECK(status IN ('PENDING', 'RUNNING', 'SUCCESS', 'FAILURE', 'TIMEOUT')),
                exitcode INTEGER,
                stdout TEXT,
                stderr TEXT,
                importid TEXT,
                createdat TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS importlogs (
                importid TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                quote TEXT NOT NULL,
                interval TEXT NOT NULL,
                exchange TEXT NOT NULL,
                starttime INTEGER,
                endtime INTEGER,
                limitparam INTEGER DEFAULT 1000,
                executionstart TEXT NOT NULL,
                executionend TEXT,
                durationseconds REAL,
                recordsreceived INTEGER DEFAULT 0,
                recordsinserted INTEGER DEFAULT 0,
                recordsupdated INTEGER DEFAULT 0,
                recordsfailed INTEGER DEFAULT 0,
                status TEXT NOT NULL CHECK(status IN ('SUCCESS', 'PARTIAL', 'FAILURE')),
                errormessage TEXT,
                errorcode INTEGER,
                triggeredby TEXT NOT NULL CHECK(triggeredby IN ('MANUAL', 'SCHEDULER', 'RETRY')),
                createdat TEXT DEFAULT CURRENT_TIMESTAMP,
                updatedat TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    await conn.commit()

    yield conn

    await conn.close()

@pytest.fixture
def sample_configured_symbol():
    """Fixture pour créer un symbole configuré de test"""
    from uuid import uuid4
    from datetime import datetime, timezone

    return {
        'symbolid': str(uuid4()),
        'symbol': 'BTC',
        'quote': 'USDT',
        'interval': '1h',
        'exchange': 'BINANCE',
        'isactive': 1,
        'createdat': datetime.now(timezone.utc).isoformat(),
        'updatedat': datetime.now(timezone.utc).isoformat()
    }

@pytest.fixture
def sample_fetchjob():
    """Fixture pour créer un FetchJob de test"""
    from uuid import uuid4
    from datetime import datetime, timezone

    return {
        'executionid': str(uuid4()),
        'taskname': 'BTCUSDT_1h_fetch',
        'symbol': 'BTCUSDT',
        'interval': '1h',
        'scheduledat': datetime.now(timezone.utc).isoformat(),
        'status': 'PENDING',
        'createdat': datetime.now(timezone.utc).isoformat()
    }
