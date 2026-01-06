# TA - DETAILED TECHNICAL ARCHITECTURE
## Cryptostory Platform

**Document Version:** 1.0  
**Date:** January 2026  
**Status:** Approved  
**Audience:** Technical Leads, Architects, DevOps, Developers

---

## 1. KEY ARCHITECTURAL DECISIONS

### 1.1 Selected Technical Stack

#### **Language & TUI Framework**
- **Python 3.10+**: Rich ecosystem, native async/await, popular among quants
- **Textual Framework**: Modern TUI framework, Rich widget library, responsive
- **Justification**: Best-in-class for TUI, mature ecosystem, cross-platform

#### **Database**
- **PostgreSQL 13+**: Robust RDBMS, ACID transactions, extensible
- **TimescaleDB extension**: Time-series optimized, hypertables, compression
- **Justification**: Hypertables for 1M+ rows/day, automatic compression, fast queries

#### **Task Orchestration**
- **Systemd Timers (Recommended)**: Modern Cron alternative, systemd-aware
- **Cron Fallback**: Support for simple OS, fallback if Systemd unavailable
- **Justification**: Systemd = integrated logging, easy monitoring, restart policies

#### **HTTP Client**
- **aiohttp**: Async HTTP, connection pooling, timeout management
- **Justification**: Non-blocking, high performance, async ecosystem integration

---

### 1.2 Architecture Pattern: Layered + Modules

```
┌───────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                          │
│  (TUI Screens, CLI Commands, REST API future)                 │
├───────────────────────────────────────────────────────────────┤
│                    SERVICE LAYER                              │
│  (Business logic, Orchestration, Scheduling)                  │
├───────────────────────────────────────────────────────────────┤
│                    DATA ACCESS LAYER                          │
│  (Database ORM, API Client, Caching)                          │
├───────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE LAYER                       │
│  (PostgreSQL, Redis, Logging, Monitoring)                     │
├───────────────────────────────────────────────────────────────┤
│                    CROSS-CUTTING                              │
│  (Config, Error Handling, Validation, Logging)                │
└───────────────────────────────────────────────────────────────┘
```

**Advantages**:
- Separation of concerns
- Testability (mock layers)
- Scalability (service decoupling)
- Maintainability (isolated changes)

---

## 2. DETAILED SYSTEM ARCHITECTURE

### 2.1 Main Components

#### **Component 1: TUI Application** `tui/`
```
TUI Instance (Textual App)
├── ConfigScreen
│   ├── Asset Selector (Dropdown)
│   ├── Quote Selector (Dropdown)
│   ├── Interval Selector (Dropdown)
│   ├── Date Range Pickers (Optional)
│   └── Submit Handler
├── MonitoringScreen
│   ├── Task Status Table
│   ├── Metrics Summary
│   ├── Rate Limit Status
│   └── Auto-refresh Timer
└── AlertsScreen
    ├── Error Log
    ├── Notifications
    └── Alert History
```

**Technology**: Textual, Rich, asyncio  
**Threading**: Single-threaded async (no GIL contention)  
**Responsiveness**: <100ms input latency

---

#### **Component 2: API Integration** `api/`

```
BinanceClient
├── HTTP Connection Pool (aiohttp)
├── Rate Limiter (Token bucket)
├── Retry Handler (Exponential backoff)
└── Error Handler (429, 418, 500 mappings)

Flow:
1. Incoming request
2. Rate limiter checks weight
3. If 90%+ throttled, sleep
4. HTTP call with timeout
5. Rate limit header processing
6. Error handling (retry/fail/escalate)
7. Response parsing
8. Return data or raise exception
```

**Code Pattern**:
```python
class BinanceClient:
    def __init__(self, base_url="https://api.binance.com"):
        self.session = None
        self.rate_limiter = RateLimiter(max_weight=5400)  # 90% of 6000
        
    async def fetch_klines(self, symbol, interval, **kwargs):
        await self.rate_limiter.acquire(weight=2)
        try:
            data = await self._http_request("/api/v3/uiKlines", 
                                          params={...})
            return KlineResponse.parse(data)
        except RateLimitError:
            await asyncio.sleep(60)  # Backoff
            return await self.fetch_klines(...)  # Retry
```

---

#### **Component 3: Database Layer** `database/`

```
DatabaseManager (Singleton)
├── Connection Pool (psycopg 3.0+, min=2, max=20)
├── Schema Manager
│   ├── Create hypertable if not exists
│   ├── Create indexes automatically
│   └── Version migrations
├── DataAccessObject (DAO)
│   ├── insert_klines_batch()
│   ├── get_latest_candlestick()
│   ├── query_range()
│   └── upsert_with_deduplication()
└── Transaction Manager
    ├── ACID guarantees
    ├── Rollback on error
    └── Logging all changes
```

**Connection Details**:
```python
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": "cryptostory",
    "user": os.getenv("DB_USER", "cryptostory"),
    "password": os.getenv("DB_PASSWORD"),
    "connect_timeout": 10,
    "min_size": 2,
    "max_size": 20,
    "max_queries": 50000,
    "max_cached_statement_lifetime": 300,
    "max_cacheable_statement_size": 15000,
}
```

---

#### **Component 4: Task Scheduler** `scheduler/`

```
TaskOrchestrator (Central coordinator)
├── Task Queue (Priority FIFO)
├── Systemd Manager
│   ├── Generate .service files
│   ├── Generate .timer files
│   └── Enable/Start timers (via systemctl or D-Bus)
├── Cron Manager (Fallback)
│   ├── Write crontab entries
│   └── Validate syntax
└── Execution Monitor
    ├── Watch systemd journal
    ├── Capture stdout/stderr
    └── Update task_executions table
```

**Scheduler Selection Logic**:
```python
if is_systemd_available():
    scheduler = SystemdScheduler()
elif has_cron_available():
    scheduler = CronScheduler()
else:
    raise RuntimeError("No scheduler available")
```

---

#### **Component 5: Validation & Quality** `validators/`

```
ValidationPipeline
├── OHLCValidator
│   ├── Check high >= {open, close, low}
│   ├── Check low <= {open, close, high}
│   ├── Check volume >= 0
│   └── Check timestamps valid
├── GapDetector
│   ├── Calculate expected interval
│   ├── Find missing candlesticks
│   └── Flag for review
└── DuplicateChecker
    ├── Check open_time uniqueness
    ├── Detect re-submissions
    └── Suggest UPSERT vs INSERT
```

---

### 2.2 Data Flow Architecture

```
┌──────────────┐
│ Scheduled    │
│ Task (cron)  │
└────────┬─────┘
         │
         ↓
┌──────────────────────────────────────┐
│   CLI Entry Point                    │
│   cryptostory fetch BTCUSDT 1h       │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Configuration Loading              │
│   - Load settings.yaml               │
│   - Validate parameters              │
│   - Get DB config                    │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Database Initialization            │
│   - Check connection                 │
│   - Ensure table exists              │
│   - Get last import time             │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Rate Limit Check                   │
│   - Query remaining weight           │
│   - Throttle if needed               │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Binance API Call                   │
│   - Fetch klines data                │
│   - Handle errors/retries            │
│   - Update rate limit state          │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Data Validation                    │
│   - Validate OHLC logic              │
│   - Check for gaps/duplicates        │
│   - Calculate checksums              │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Database Insertion                 │
│   - Create import_logs entry         │
│   - UPSERT klines batch              │
│   - Log any errors                   │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Post-Processing                    │
│   - Calculate statistics             │
│   - Send alerts if errors            │
│   - Update monitoring metrics        │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Success / Failure Result           │
│   - Return exit code                 │
│   - Log to stdout/stderr             │
└──────────────────────────────────────┘
```

---

## 3. JUSTIFIED TECHNOLOGICAL CHOICES

### 3.1 Why PostgreSQL + TimescaleDB?

| Criteria | Alternative | Choice | Justification |
|--------|-------------|--------|---------------|
| **Time-series perf** | InfluxDB, QuestDB | TimescaleDB | Hypertables + automatic compression |
| **ACID guarantees** | NoSQL (Mongo) | PostgreSQL | Native ACID required for audit |
| **Cost** | Cloud DB (AWS RDS) | Self-hosted | Cost-effective, full control |
| **Scaling** | Manual sharding | Hypertables | Transparent partitioning |
| **Queries** | Limited (time-series only) | PostgreSQL | Full SQL, joins, aggregations |

**Recommended Configuration**:
```yaml
postgresql:
  version: 13.10+
  timescaledb_version: 2.10+
  shared_preload_libraries:
    - timescaledb
  max_connections: 100
  shared_buffers: 4GB
  effective_cache_size: 12GB
  work_mem: 16MB
  maintenance_work_mem: 1GB
  random_page_cost: 1.1
```

---

### 3.2 Why Systemd vs Cron?

| Aspect | Cron | Systemd Timer |
|-------|------|---------------|
| **Logging** | Limited syslog | Full, structured journal |
| **Monitoring** | None native | systemctl status, metrics |
| **Restart policies** | Manual | Automatic (OnFailure) |
| **Timezone** | UTC only | Timezone-aware |
| **Accuracy** | Minute granularity | Sub-second possible |
| **Dependency mgmt** | Bash scripts | Unit dependencies (After, Requires) |

**Recommendation**: Systemd Timer in production, Cron fallback for legacy OS

---

### 3.3 Why Textual for TUI?

| Framework | Rich UX | Async | Responsive | Modern |
|----------|---------|-------|------------|--------|
| **Textual** | ⭐⭐⭐ | ✅ | ✅ | ✅ |
| **curses** | ⭐ | ❌ | ❌ | ❌ |
| **Click** | ⭐⭐ | ⚠️ | ⚠️ | ⚠️ |
| **prompt_toolkit** | ⭐⭐⭐ | ⚠️ | ⚠️ | ✅ |

Textual = best UX/maintenance ratio, modern, active open-source

---

## 4. INFRASTRUCTURE AND DEPLOYMENT

### 4.1 Infrastructure Requirements

#### **Minimum (Dev/Test)**
```
CPU: 2 cores
RAM: 4 GB
Disk: 50 GB SSD (PostgreSQL data)
Network: 1 Mbps min (Binance API latency <200ms)
OS: Ubuntu 20.04 LTS / Debian 11+
```

#### **Recommended (Production)**
```
CPU: 4+ cores
RAM: 16 GB (8GB PostgreSQL, 8GB other)
Disk: 500 GB+ SSD
  - 300 GB for OHLC data (5 years, 100 pairs)
  - 50 GB for backups
  - 150 GB free space
Network: 10 Mbps (redundancy)
OS: Ubuntu 22.04 LTS
PostgreSQL: 15+ (latest stable)
```

---

### 4.2 Deployment Architecture

```
┌─────────────────────────────────────────┐
│  Deployment Target (Linux Server)       │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Cryptostory Application          │  │
│  │ ├── TUI (Textual)                │  │
│  │ ├── CLI Commands                 │  │
│  │ └── Daemon (Systemd service)     │  │
│  └──────────────────────────────────┘  │
│           ↓ (Python)                   │
│  ┌──────────────────────────────────┐  │
│  │ Database (PostgreSQL + TimeScale)│  │
│  │ - cryptostory DB                 │  │
│  │ - Hypertables (BINANCE_*_*)      │  │
│  │ - IMPORT_LOGS, API_ERRORS, etc.  │  │
│  └──────────────────────────────────┘  │
│           ↓ (TCP 5432)                 │
│  ┌──────────────────────────────────┐  │
│  │ Storage (Disk/SSD)               │  │
│  │ - PostgreSQL WAL logs            │  │
│  │ - Data files                     │  │
│  │ - Backups                        │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Systemd Integration              │  │
│  │ - cryptostory.service            │  │
│  │ - cryptostory-fetch-*.timer      │  │
│  │ - systemd.journal logging        │  │
│  └──────────────────────────────────┘  │
│                                         │
│  Network Interface:                    │
│  └─→ Binance API (api.binance.com)    │
│  └─→ SMTP (email alerts)              │
│                                         │
└─────────────────────────────────────────┘
```

---

### 4.3 Installation & Setup Procedure

#### **Step 1: System Prerequisites**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.10 python3.10-venv python3-pip
sudo apt-get install -y postgresql postgresql-13-timescaledb
sudo apt-get install -y systemd (usually pre-installed)

# Add timescaledb to PostgreSQL
sudo -u postgres psql -c "CREATE EXTENSION timescaledb CASCADE;"
```

#### **Step 2: Application Installation**
```bash
# Clone/Download
git clone https://github.com/yourusername/cryptostory.git
cd cryptostory

# Virtual environment
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup configuration
cp config/settings.yaml.example config/settings.yaml
# Edit settings.yaml with actual DB credentials
```

#### **Step 3: Database Setup**
```bash
# Create database
sudo -u postgres createdb cryptostory

# Load schema
psql -U cryptostory -d cryptostory -f sql/schema.sql

# Create TimescaleDB hypertables (auto-created on first insert)
```

#### **Step 4: Run Application**
```bash
# TUI Interactive
python -m cryptostory.tui

# CLI Command
python -m cryptostory.cli fetch BTCUSDT 1h

# Systemd service installation
sudo cp systemd/cryptostory.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cryptostory
```

---

## 5. IMPLEMENTED PATTERNS AND BEST PRACTICES

### 5.1 Error Handling Pattern

```python
class CryptostoryException(Exception):
    """Base exception"""
    
class RateLimitError(CryptostoryException):
    """Recoverable error - retry"""
    
class IPBanError(CryptostoryException):
    """Non-recoverable - requires manual intervention"""
    
class DataValidationError(CryptostoryException):
    """Invalid data - skip record, log"""
    
class DatabaseError(CryptostoryException):
    """DB issue - transaction rollback"""

# Usage:
try:
    data = await api_client.fetch_klines(...)
except RateLimitError:
    await asyncio.sleep(60)
    return await retry_fetch(...)
except IPBanError:
    logger.critical("IP banned from Binance")
    send_email_alert("IP Ban detected")
    raise
except DataValidationError as e:
    logger.warning(f"Data validation failed: {e}")
    skip_record()
```

---

### 5.2 Async/Await Pattern (Non-blocking)

```python
async def fetch_multiple_symbols(symbols: List[str], interval: str):
    """Fetch multiple symbols concurrently (max 5 parallel)"""
    
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
    
    async def fetch_with_semaphore(symbol):
        async with semaphore:
            return await api_client.fetch_klines(symbol, interval)
    
    tasks = [fetch_with_semaphore(s) for s in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

**Advantage**: No threads, no GIL, easy scaling to 100+ symbols

---

### 5.3 Dependency Injection Pattern

```python
class Application:
    def __init__(self, config: Config, db: Database, api_client: BinanceClient):
        self.config = config
        self.db = db
        self.api_client = api_client
    
    async def run(self):
        # Use injected dependencies
        data = await self.api_client.fetch_klines(...)
        await self.db.insert(...)

# Instantiation:
config = Config.from_file("settings.yaml")
db = Database(config.db)
api = BinanceClient(config.api)
app = Application(config, db, api)
```

**Advantage**: Testable, mockable, loose coupling

---

## 6. PERFORMANCE AND SCALABILITY

### 6.1 Performance Targets

| Operation | Target | Current Estimate |
|-----------|--------|------------------|
| **Fetch 1000 klines** | < 5 sec | 2–3 sec (network bound) |
| **Insert 1000 rows** | < 1 sec | 0.5 sec |
| **Query last 1000 days** | < 100 ms | 50 ms (indexed) |
| **UI responsiveness** | < 100 ms | 50 ms (async) |
| **Memory per task** | < 100 MB | 50 MB |

---

### 6.2 Scalability to 100+ Symbols

```
Scenario: 100 symbols × 5 timeframes = 500 tasks

Rate Limiting:
  6000 weight/min ÷ 2 weight/request = 3000 max requests/min
  500 tasks = 500 requests/min needed
  3000/500 = 6x headroom ✅
  
Database:
  Each task = ~1000 rows/import
  1 month = 30 imports/symbol
  100 symbols × 5 timeframes × 1000 rows × 30 = 15M rows/month
  TimescaleDB compression: 15M → ~50 GB/year ✅
  
Memory:
  App: 200 MB base
  Per symbol × 5: 50 MB
  100 symbols = 200 + (100×50MB) = 5 GB peak ✅
  
CPU:
  Mostly I/O wait (network + DB)
  Low CPU utilization (async)
  4 cores sufficient
```

---

## 7. SECURITY AND COMPLIANCE

### 7.1 Security Measures

| Aspect | Measure |
|-------|---------|
| **API Credentials** | Environment variables only, never hardcoded |
| **DB Credentials** | Encrypted in .env, OS-level permissions |
| **Data in Transit** | HTTPS only (Binance API enforced) |
| **Data at Rest** | PostgreSQL encryption (pgcrypto) optional |
| **Audit Logs** | All imports/errors logged immutably |
| **Input Validation** | Strict parameter validation before API calls |

### 7.2 Data Protection

- **No PII stored**: Only market data (OHLCV)
- **GDPR Compliant**: No personal data collection
- **Data Retention**: Configurable (default 5 years)
- **Backups**: Recommended automated (WAL-E, pg_basebackup)

---

## 8. MONITORING AND OBSERVABILITY

### 8.1 Logging Strategy

```python
logger.info("Task started", extra={
    "symbol": "BTCUSDT",
    "interval": "1h",
    "import_id": import_id,
    "user": "scheduler",
    "timestamp": datetime.now().isoformat()
})

# Output to systemd journal (structured JSON)
# Queryable via: journalctl -u cryptostory SERVICE
```

### 8.2 Metrics Collected

- Import success rate (%)
- Average import duration (sec)
- Rate limit utilization (%)
- Error frequency by type
- Data integrity scores

---

## CONCLUSION

This architecture is designed to be:
- **Scalable**: Handle 100+ symbols/timeframes without issue
- **Reliable**: ACID guarantees, error recovery, audit trails
- **Maintainable**: Layered design, async/await, DI pattern
- **Observable**: Structured logging, metrics, monitoring
- **Secure**: No hardcoded secrets, immutable audit trails

**Approved by:** Technical Architect _________________ Date: _______
