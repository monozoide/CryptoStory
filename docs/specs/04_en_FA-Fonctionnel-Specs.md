# FA - DETAILED FUNCTIONAL SPECIFICATIONS AND DATA MODEL
## Cryptostory Platform

**Document Version:** 1.0  
**Date:** January 2026  
**Status:** Approved  
**Audience:** Developers, QA, Technical Leads

---

## 1. GLOBAL FUNCTIONAL ARCHITECTURE

### 1.1 Main Business Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN FLOW                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. User launches TUI                                        │
│         ↓                                                     │
│  2. Initial configuration (symbol, interval, dates, etc.)   │
│         ↓                                                     │
│  3. Config validation + available data validation           │
│         ↓                                                     │
│  4. DB table creation (if not exists)                        │
│         ↓                                                     │
│  5. Binance API call (with rate limit handling)              │
│         ↓                                                     │
│  6. JSON response parsing, data validation                   │
│         ↓                                                     │
│  7. Batch insert into DB (ACID transaction)                  │
│         ↓                                                     │
│  8. Successful import log in IMPORT_LOGS                     │
│         ↓                                                     │
│  9. Systemd Timer/Cron creation for periodic collection      │
│         ↓                                                     │
│  10. User sees OK monitoring dashboard                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Main Functional Modules

```
cryptostory/
├── tui/                      # Terminal User Interface (Textual)
│   ├── config_screen.py      # Symbol/interval/dates configuration
│   ├── monitoring_screen.py  # Task monitoring dashboard
│   └── alerts_screen.py      # Error/alerts display
│
├── api/                      # Binance API Integration
│   ├── binance_client.py     # Binance HTTP client
│   ├── rate_limiter.py       # Rate limit management
│   └── retry_handler.py      # Exponential retry logic
│
├── database/                 # Data Persistence
│   ├── connection.py         # PostgreSQL + TimescaleDB
│   ├── schema.py             # Dynamic table creation
│   ├── data_manager.py       # Insert/Update/Query
│   └── migrations.py         # DB schema versioning
│
├── scheduler/                # Task Orchestration
│   ├── task_orchestrator.py  # Manage 10–100+ tasks
│   ├── systemd_manager.py    # Create Systemd timers
│   ├── cron_manager.py       # Create Cron jobs
│   └── task_queue.py         # Queue + priority management
│
├── validators/               # Data Validation
│   ├── ohlc_validator.py     # OHLC logic checks
│   ├── gap_detector.py       # Temporal gap detection
│   └── duplicate_checker.py  # Duplicate detection
│
├── logging/                  # Logging + Audit
│   ├── audit_logger.py       # IMPORT_LOGS + API_ERRORS
│   ├── structured_logs.py    # JSON structured logging
│   └── alert_manager.py      # Email/Webhook alerts
│
└── config/                   # Configuration Management
    ├── settings.yaml         # Global settings
    ├── symbols_list.json     # Supported symbols
    └── error_codes.json      # Error mapping
```

---

## 2. DETAILED DATA MODEL

### 2.1 Core Tables (OHLCV)

#### Table: `BINANCE_<SYMBOL>_<INTERVAL>`
Example: `BINANCE_BTCUSDT_1h`, `BINANCE_ETHUSDT_1m`, etc.

```sql
CREATE TABLE IF NOT EXISTS BINANCE_BTCUSDT_1h (
  -- Primary Keys & Time
  open_time TIMESTAMPTZ PRIMARY KEY,
  
  -- OHLCV Data
  open_price NUMERIC(20, 8) NOT NULL CHECK (open_price > 0),
  high_price NUMERIC(20, 8) NOT NULL CHECK (high_price > 0),
  low_price NUMERIC(20, 8) NOT NULL CHECK (low_price > 0),
  close_price NUMERIC(20, 8) NOT NULL CHECK (close_price > 0),
  base_volume NUMERIC(20, 8) NOT NULL CHECK (base_volume >= 0),
  
  -- Additional Fields
  close_time TIMESTAMPTZ NOT NULL CHECK (close_time > open_time),
  quote_asset_volume NUMERIC(20, 8) NOT NULL CHECK (quote_asset_volume >= 0),
  number_of_trades INT NOT NULL CHECK (number_of_trades >= 0),
  taker_buy_base_volume NUMERIC(20, 8) NOT NULL CHECK (taker_buy_base_volume >= 0),
  taker_buy_quote_volume NUMERIC(20, 8) NOT NULL CHECK (taker_buy_quote_volume >= 0),
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT now(),
  import_id UUID REFERENCES import_logs(import_id),
  
  -- Validation
  is_validated BOOLEAN DEFAULT false,
  validation_errors TEXT
) PARTITION BY RANGE (open_time);

-- Convert to TimescaleDB Hypertable
SELECT create_hypertable('BINANCE_BTCUSDT_1h', 'open_time', if_not_exists => TRUE);

-- Performance indexes
CREATE INDEX idx_binance_btcusdt_1h_open_time 
  ON BINANCE_BTCUSDT_1h (open_time DESC);
CREATE INDEX idx_binance_btcusdt_1h_import_id 
  ON BINANCE_BTCUSDT_1h (import_id);
```

**Integrity Rules:**
- `high_price >= max(open_price, close_price, low_price)`
- `low_price <= min(open_price, close_price, high_price)`
- `close_time > open_time`
- `all volumes >= 0`
- `no negative prices`

**Sample Data:**
```
open_time             | open    | high    | low     | close   | volume
2026-01-05 14:00:00   | 42500.5 | 42850.0 | 42400.0 | 42750.3 | 1245.67
2026-01-05 15:00:00   | 42750.3 | 43000.0 | 42700.0 | 42950.5 | 1356.89
```

---

### 2.2 Metadata and Audit Tables

#### Table: `import_logs`
Records each import with its result

```sql
CREATE TABLE import_logs (
  import_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Import Configuration
  symbol VARCHAR(20) NOT NULL,      -- e.g. BTCUSDT
  interval VARCHAR(5) NOT NULL,     -- e.g. 1h
  exchange VARCHAR(20) NOT NULL,    -- e.g. BINANCE
  
  -- Time Range
  start_time BIGINT,                -- Optional: Unix timestamp (ms)
  end_time BIGINT,                  -- Optional: Unix timestamp (ms)
  limit_param INT DEFAULT 1000,     -- Used limit
  
  -- Execution Details
  execution_start TIMESTAMPTZ NOT NULL DEFAULT now(),
  execution_end TIMESTAMPTZ,
  duration_seconds FLOAT,
  
  -- Results
  records_imported INT DEFAULT 0,
  records_failed INT DEFAULT 0,
  api_requests_count INT DEFAULT 0,
  status VARCHAR(20) NOT NULL,      -- SUCCESS, PARTIAL, FAILURE
  
  -- Data Quality
  checksum_sha256 VARCHAR(64),
  validation_passed BOOLEAN,
  error_count INT DEFAULT 0,
  
  -- Error Handling
  error_message TEXT,
  rate_limit_used INT DEFAULT 0,
  
  -- Metadata
  user_who_triggered VARCHAR(100),
  triggered_by VARCHAR(20),         -- MANUAL, SCHEDULER, RETRY
  
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_import_logs_symbol_interval 
  ON import_logs(symbol, interval, execution_start DESC);
CREATE INDEX idx_import_logs_status 
  ON import_logs(status);
```

**Possible Business Queries:**
```sql
-- Which imports failed yesterday?
SELECT * FROM import_logs 
WHERE status = 'FAILURE' AND execution_start > now() - interval '24 hours';

-- Audit trail for a specific symbol
SELECT * FROM import_logs 
WHERE symbol = 'BTCUSDT' AND interval = '1h' 
ORDER BY execution_start DESC LIMIT 100;

-- Success rate over the last 7 days
SELECT 
  interval,
  COUNT(*) as total_imports,
  SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
  ROUND(100.0 * SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM import_logs
WHERE execution_start > now() - interval '7 days'
GROUP BY interval;
```

---

#### Table: `api_errors`
Records each API error for debugging and trending

```sql
CREATE TABLE api_errors (
  error_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  import_id UUID NOT NULL REFERENCES import_logs(import_id),
  
  -- Error Details
  http_code INT NOT NULL,           -- 429, 418, 500, etc.
  error_code INT,                   -- Binance error code (-1003, etc.)
  error_message TEXT NOT NULL,      -- Exact error from Binance
  error_category VARCHAR(50),       -- RATE_LIMIT, IP_BAN, BAD_REQUEST, SERVER_ERROR
  
  -- Context
  symbol VARCHAR(20) NOT NULL,
  interval VARCHAR(5) NOT NULL,
  start_time BIGINT,
  end_time BIGINT,
  
  -- Resolution
  retry_attempted BOOLEAN DEFAULT false,
  retry_count INT DEFAULT 0,
  resolved_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_api_errors_error_code 
  ON api_errors(error_code);
CREATE INDEX idx_api_errors_created_at 
  ON api_errors(created_at DESC);
CREATE INDEX idx_api_errors_symbol 
  ON api_errors(symbol);
```

**Diagnostic Queries:**
```sql
-- Rate limit errors (429) over recent days
SELECT * FROM api_errors 
WHERE http_code = 429 AND created_at > now() - interval '7 days'
ORDER BY created_at DESC;

-- Error patterns
SELECT error_code, COUNT(*) as occurrences, MAX(created_at)
FROM api_errors
GROUP BY error_code
HAVING COUNT(*) > 5
ORDER BY occurrences DESC;
```

---

#### Table: `task_executions`
Detailed history of each scheduled task execution

```sql
CREATE TABLE task_executions (
  execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Task Definition
  task_name VARCHAR(100) NOT NULL,  -- e.g. BTCUSDT_1h_fetch
  symbol VARCHAR(20) NOT NULL,
  interval VARCHAR(5) NOT NULL,
  
  -- Execution Timeline
  scheduled_at TIMESTAMPTZ NOT NULL,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  
  -- Result
  status VARCHAR(20),               -- PENDING, RUNNING, SUCCESS, FAILURE, TIMEOUT
  exit_code INT,
  stdout TEXT,
  stderr TEXT,
  
  -- Associated Import
  import_id UUID REFERENCES import_logs(import_id),
  
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_task_executions_symbol_interval 
  ON task_executions(symbol, interval, scheduled_at DESC);
```

---

### 2.3 ER Relational Diagram

```
┌──────────────────────────────────────────────────┐
│         import_logs                              │
│ ─────────────────────────────────────────────    │
│ import_id (PK, UUID)                             │
│ symbol, interval, exchange                       │
│ execution_start, execution_end                   │
│ records_imported, status                         │
│ checksum_sha256, error_message                   │
└──────────────────────────────────────────────────┘
         ↑                          ↑
         │ (import_id FK)          │ (import_id FK)
         │                         │
┌────────────────────────┐  ┌──────────────────┐
│ BINANCE_BTCUSDT_1h     │  │   api_errors     │
│ ───────────────────    │  │ ──────────────── │
│ open_time (PK)         │  │ error_id (PK)    │
│ open, high, low, close │  │ http_code        │
│ volume, quote_volume   │  │ error_message    │
│ import_id (FK)         │  │ error_category   │
│                        │  │ symbol, interval │
│ (Similar for all pairs)│  │                  │
└────────────────────────┘  └──────────────────┘

┌──────────────────────────────────────────────┐
│      task_executions                         │
│ ──────────────────────────────────────────── │
│ execution_id (PK)                            │
│ task_name, symbol, interval                  │
│ scheduled_at, started_at, completed_at       │
│ status, exit_code, stdout, stderr            │
│ import_id (FK)                               │
└──────────────────────────────────────────────┘
```

---

## 3. FUNCTIONAL SPECIFICATIONS BY MODULE

### 3.1 TUI Module – Configuration Screen

#### Screen 1: Initial Configuration

```
╔═══════════════════════════════════════════════════════════╗
║         CRYPTOSTORY - INITIAL CONFIGURATION               ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Asset (Required):                                       ║
║  ┌──────────────────────────────────────────────────┐   ║
║  │ BTC ▼                  [View full list]          │   ║
║  └──────────────────────────────────────────────────┘   ║
║                                                           ║
║  Quote Currency (Required):                              ║
║  ┌──────────────────────────────────────────────────┐   ║
║  │ USDT ▼                                           │   ║
║  └──────────────────────────────────────────────────┘   ║
║                                                           ║
║  Full Symbol: BTCUSDT ✅ (valid symbol)                  ║
║                                                           ║
║  Timeframe (Required):                                  ║
║  ┌──────────────────────────────────────────────────┐   ║
║  │ 1h ▼                                             │   ║
║  │  - 1m (minute)                                   │   ║
║  │  - 1h (hour)                                     │   ║
║  │  - 1d (day)                                      │   ║
║  │  - 1w (week)                                     │   ║
║  │  - 1M (month)                                    │   ║
║  └──────────────────────────────────────────────────┘   ║
║                                                           ║
║  [TAB = Next Field] [ENTER = Submit]                     ║
╚═══════════════════════════════════════════════════════════╝
```

#### Features:
- **Asset Dropdown**: List of 100+ assets (searchable)
- **Quote Dropdown**: USDT (primary), USDC, EUR, BUSD, etc.
- **Real-time Symbol**: Displays full symbol during input
- **Validation**: Checks that the symbol exists on Binance (API query)
- **Navigation**: TAB/SHIFT+TAB, ENTER to confirm

#### Pseudo Code:
```python
class ConfigScreen(Screen):
  def compose(self) -> ComposeResult:
    yield Label("Asset:")
    yield Select(["BTC", "ETH", "ADA", ...], id="asset_select")
    yield Label("Quote:")
    yield Select(["USDT", "USDC", "EUR"], id="quote_select")
    yield Label(f"Symbol: {self.symbol_complete}", id="symbol_display")
    yield Label("Timeframe:")
    yield Select(["1m", "1h", "1d", "1w", "1M"], id="interval_select")
    yield Button("Next →", id="next_btn")
    
  def on_select_changed(self, event: Select.Changed):
    self.update_symbol_display()
    self.validate_symbol_on_binance()
```

---

## CONCLUSION

This document specifies the functional and structural details required to implement Cryptostory. The modules are decoupled and independently testable.

**Approved by:** Functional Analyst _________________ Date: _______
