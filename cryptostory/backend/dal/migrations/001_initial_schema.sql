-- Table configured_symbols
CREATE TABLE IF NOT EXISTS configured_symbols (
    symbolid TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    quote TEXT NOT NULL,
    interval TEXT NOT NULL,
    exchange TEXT NOT NULL DEFAULT 'BINANCE',
    isactive INTEGER DEFAULT 1,
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    updatedat TEXT DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_configured_symbol UNIQUE(exchange, symbol, quote, interval)
);

CREATE INDEX idx_configured_symbols_active ON configured_symbols(isactive) WHERE isactive = 1;

-- Table taskexecutions (pour FetchJob)
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
);

CREATE INDEX idx_taskexecutions_symbol_interval ON taskexecutions(symbol, interval, scheduledat DESC);
CREATE INDEX idx_taskexecutions_status ON taskexecutions(status) WHERE status IN ('RUNNING', 'PENDING', 'FAILURE');

-- Table importlogs
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
    recordsrequested INTEGER,
    recordsreceived INTEGER DEFAULT 0,
    recordsinserted INTEGER DEFAULT 0,
    recordsupdated INTEGER DEFAULT 0,
    recordsfailed INTEGER DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('SUCCESS', 'PARTIAL', 'FAILURE')),
    checksumsha256 TEXT,
    validationpassed INTEGER DEFAULT 0,
    errorcount INTEGER DEFAULT 0,
    errormessage TEXT,
    errorcode INTEGER,
    ratelimitused INTEGER DEFAULT 0,
    ratelimitafter INTEGER DEFAULT 0,
    userwhotriggered TEXT,
    triggeredby TEXT NOT NULL CHECK(triggeredby IN ('MANUAL', 'SCHEDULER', 'RETRY')),
    createdat TEXT DEFAULT CURRENT_TIMESTAMP,
    updatedat TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_importlogs_symbol_interval ON importlogs(symbol, interval, executionstart DESC);
CREATE INDEX idx_importlogs_status ON importlogs(status) WHERE status IN ('FAILURE', 'PARTIAL');
