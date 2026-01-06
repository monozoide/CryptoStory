# PO - USER STORIES, ACCEPTANCE CRITERIA, AND ROADMAP
## Cryptostory Platform - Crypto OHLCV Data

**Document Version:** 1.0  
**Date:** January 2026  
**Status:** Validated Product Backlog  
**Audience:** Agile Team, Product Owner, Developers

---

## 1. PERSONAS AND USER JOURNEY

### 1.1 Key Personas

#### **Persona 1: Professional Quantitative Trader**
- **Name**: Alex (Quant Trader)
- **Profile**: 5+ years in algorithmic trading, €500K+ assets under management
- **Need**: Reliable access to complete historical data (5+ years) for multi-timeframe backtesting
- **Pain Points**: Binance rate limits, data loss, API latency
- **Success Metric**: Zero data loss, full sync in <5 minutes for 100 pairs

#### **Persona 2: Data Engineer / FinTech**
- **Name**: Jordan (Data Eng)
- **Profile**: Data pipeline engineer, 50-person FinTech startup
- **Need**: Scalable infrastructure, monitoring, integration with existing pipelines
- **Pain Points**: Manual rate limit handling, difficult monitoring, lack of alerting
- **Success Metric**: Real-time monitoring, proactive alerts, 0 manual intervention

#### **Persona 3: Retail Trader**
- **Name**: Maya (Retail Trader)
- **Profile**: Independent trader, personal crypto portfolio
- **Need**: Simple and free solution, no advanced dev skills required
- **Pain Points**: API complexity, cloud costs, difficult setup
- **Success Metric**: Installation in <10 minutes, intuitive no-code usage

#### **Persona 4: Researcher / Academic**
- **Name**: Prof. Chen (Researcher)
- **Profile**: Academic studying crypto markets, peer-reviewed publications
- **Need**: Public data, reproducibility, easy export, open-source license
- **Pain Points**: Professional data costs, limited reproducibility, restricted access
- **Success Metric**: Certified data, CSV/Parquet export, MIT license

---

## 2. DETAILED PRODUCT BACKLOG

### 2.1 EPIC 1: Configuration and Onboarding (P1 - MVP)

#### **User Story 1.1: Initial configuration via TUI**
```
As a trader
I want to configure symbols and timeframes via a TUI interface
So that I can start data collection without touching the code

Acceptance Criteria:
☐ TUI displays a structured configuration screen
☐ Dropdown list to select asset (ADA, BTC, ETH, etc.)
☐ Dropdown list to select quote (USDT, USDC, EUR)
☐ Full symbol (e.g. AXSUSDT) displayed in real time
☐ Validation: symbol is mandatory, non-empty
☐ Dropdown list for timeframe (1m, 1h, 1d, 1w, 1M)
☐ Validation: timeframe is mandatory
☐ Visual feedback: ✅ valid symbol, ❌ invalid symbol
☐ TAB/SHIFT+TAB navigation between fields
☐ Visible focus with distinct color
☐ Clear error message if data is missing
```

#### **User Story 1.2: Optional dates and timezone**
```
As a quantitative trader
I want to filter by date ranges and define my timezone
So that I can obtain data for a specific period in my temporal context

Acceptance Criteria:
☐ Optional startTime field (date picker or epoch input)
☐ Optional endTime field (date picker or epoch input)
☐ Validation: if both dates are filled, endTime > startTime
☐ Visual warning if the period implies >1000 records
  (e.g. "120 days in 1m = 172,800 candlesticks, max API 1000, chunking required")
☐ Display calculation of record count before submission
☐ Timezone dropdown -12:00 to +14:00 (default: UTC)
☐ Explanation: "timestamps in UTC, timezone for display only"
☐ If startTime or endTime not provided, fetch recent data only
```

#### **User Story 1.3: Record limit**
```
As a data engineer
I want to configure the maximum number of records per request
So that I can control requests and chunking

Acceptance Criteria:
☐ Limit field with default value 1000 (Binance max)
☐ Validation: limit between 1 and 1000
☐ Explanatory message: "Binance max 1000, lower value = more requests"
☐ Impact display of estimated request cost if limit is low
```

#### **User Story 1.4: Import lists from files**
```
As a trader with a portfolio of 100+ pairs
I want to import my symbol list from a CSV file
So that I can configure quickly without manual input

Acceptance Criteria:
☐ Support CSV format (symbol1, symbol2...) or JSON
☐ "Import file" field with file picker
☐ Validation of imported symbols (valid XXXUSDT format?)
☐ Display number of imported symbols
☐ Option to merge with existing dropdown or overwrite
☐ Clear error message if file format is invalid
☐ Support relative + absolute paths
```

---

### 2.2 EPIC 2: Database and Persistence (P1 - MVP)

#### **User Story 2.1: Dynamic table creation**
```
As a data engineer
I want the platform to automatically create DB tables
So that I do not manage the schema manually

Acceptance Criteria:
☐ For each (exchange, symbol, interval), create table e.g. BINANCE_AXSUSDT_1h
☐ Table schema:
  - open_time (TIMESTAMP, PRIMARY KEY)
  - open_price (NUMERIC 20,8)
  - high_price (NUMERIC 20,8)
  - low_price (NUMERIC 20,8)
  - close_price (NUMERIC 20,8)
  - volume (NUMERIC 20,8)
  - close_time (TIMESTAMP)
  - quote_asset_volume (NUMERIC 20,8)
  - number_of_trades (INT)
  - taker_buy_base_volume (NUMERIC 20,8)
  - taker_buy_quote_volume (NUMERIC 20,8)
☐ Index on symbol, open_time for fast queries
☐ TimescaleDB hypertable for automatic partitioning
☐ TUI validation: "Table BINANCE_AXSUSDT_1h created ✅"
☐ If table already exists, skip without error
☐ ACID transactions to guarantee consistency
```

#### **User Story 2.2: Import logging and metadata**
```
As a data steward
I want each import to be tracked with complete metadata
So that I can audit and debug imports

Acceptance Criteria:
☐ Create IMPORT_LOGS table with:
  - import_id (UUID, PK)
  - table_name (e.g. BINANCE_AXSUSDT_1h)
  - start_time, end_time (import datetime)
  - records_count (number of imported candlesticks)
  - status (SUCCESS, FAILURE, PARTIAL)
  - error_message (if error)
  - request_count (number of API calls)
☐ Index import_id -> data tables for traceability
☐ Foreign key relationship between IMPORT_LOGS and data tables
☐ Query possible: "Which imports failed yesterday?"
☐ Audit trail exportable to CSV
```

#### **User Story 2.3: API error handling in DB**
```
As a monitoring engineer
I want each API error to be stored in the database
So that I can detect patterns and alert

Acceptance Criteria:
☐ Create API_ERRORS table with:
  - error_id (UUID)
  - import_id (FK)
  - http_code (429, 500, etc.)
  - error_code (e.g. -1003 Weight exceeded)
  - error_message (exact Binance text)
  - timestamp
  - symbol, interval, start_time, end_time
☐ Index error_code for error-type queries
☐ Alert trigger if 429 (rate limit exceeded)
☐ Dashboard query: "429 errors last 24h"
```

---

### 2.3 EPIC 3: Binance Data Retrieval (P1 - MVP)

#### **User Story 3.1: Binance uiKlines API call**
```
As a data collector
I want the platform to call the Binance uiKlines API
So that I can retrieve OHLCV candlesticks

Acceptance Criteria:
☐ Endpoint: https://api.binance.com/api/v3/uiKlines
☐ Parameters: symbol, interval, startTime (optional), endTime (optional), limit
☐ If startTime AND endTime absent: fetch 1000 most recent
☐ If startTime AND endTime present: adjust parameters
☐ Correct JSON parsing (11 fields per candlestick)
☐ Error handling: 404 (invalid symbol), 429 (rate limit), 418 (IP ban)
☐ Retry logic with exponential backoff for temporary errors
☐ Default timeout 10s
☐ Correct User-Agent header (e.g. Cryptostory/1.0)
```

#### **User Story 3.2: Rate limit management**
```
As an infrastructure engineer
I want the platform to strictly respect Binance rate limits
So that I avoid bans and interruptions

Acceptance Criteria:
☐ Monitor x-mbx-used-weight-1m header
☐ Limit: 6000 weight per minute (Binance standard)
☐ Each uiKlines request = 2 weight
☐ Calculation: max_requests_per_minute = 6000 / 2 = 3000
☐ If approaching 90% limit: automatically throttle requests
☐ If hitting 100%: backoff 60s then retry
☐ Logging: "Rate limit used: 2450/6000 (40.8%)"
☐ Prediction: "Estimated time to reset: 45s"
☐ Configurable: rate_limit_strategy (strict, moderate, aggressive)
```

#### **User Story 3.3: Chunking for long periods**
```
As a quant backtrader
I want to retrieve 5 years of 1m data without errors
So that I can perform full backtesting

Acceptance Criteria:
☐ If (endTime - startTime) > 1000 candlesticks for given interval:
  - Automatically split into chunks
  - Example: 5 years 1m = 2,628,000 candlesticks
  - Split into 2628 requests of 1000 each
☐ Progress display: "Fetching chunk 124/2628 (4.7%)"
☐ Intelligent parallelization (max 5 in-flight requests)
☐ Rate limits respected even with chunking
☐ Temporary in-memory accumulation of results
☐ Batch DB insertion at the end (atomic transaction)
☐ Recovery on interruption: resume from last successful chunk
```

---

### 2.4 EPIC 4: Scheduled Task Orchestration (P1 - MVP)

#### **User Story 4.1: Systemd vs Cron task generation**
```
As a system ops engineer
I want the platform to create scheduled tasks
So that data is collected automatically on a schedule

Acceptance Criteria:
☐ TUI option: "Scheduler: Systemd Timer or Cron?"
☐ If Systemd:
  - Create /etc/systemd/system/cryptostory-SYMBOL-INTERVAL.service
  - Create /etc/systemd/system/cryptostory-SYMBOL-INTERVAL.timer
  - Timer defined by interval (e.g. 1h for 1h data = hourly)
  - Service script: API call, DB insertion, logging
☐ If Cron:
  - Add line to user crontab
  - Format: "0 * * * * /usr/local/bin/cryptostory fetch AXSUSDT 1h"
  - For 1m: "*/1 * * * *", for 1d: "0 0 * * *", etc.
☐ Post-creation validation: manually test the task
☐ Display: "✅ Task AXSUSDT 1h created (Systemd Timer, runs on the hour)"
☐ Option to view generated command before commit
```

#### **User Story 4.2: Managing 10–100+ parallel tasks**
```
As a platform engineer
I want the system to intelligently orchestrate 100+ tasks
So that Binance or the DB is not overloaded

Acceptance Criteria:
☐ Interval-to-execution-time mapping to avoid spikes:
  - 1m: run every minute (distributed)
  - 1h: run once per hour at :00
  - 1d: run at 00:00 UTC
  - 1w: run every Monday 00:00 UTC
  - 1M: run on the 1st of the month at 00:00 UTC
☐ Staggering: if 50 symbols at 1h, do not launch all at :00, but 1 every 1–2 minutes
☐ Max parallelism: configurable (default 5 simultaneous)
☐ Priority queue (1d > 1h > 1m)
☐ Lockfile per (symbol, interval) to prevent double runs
☐ Monitoring: "Currently running: 3/5 tasks, 47 queued"
☐ Dashboard displays next scheduled runs
```

#### **User Story 4.3: Task monitoring and alerting**
```
As a platform ops engineer
I want to see the status of each scheduled task
So that I can detect problems before they escalate

Acceptance Criteria:
☐ TUI dashboard table:
  | Symbol | Interval | Last Run | Status | Next Run | Error |
  | AXSUSDT | 1h | 2026-01-05 14:00 | ✅ | 2026-01-05 15:00 | - |
  | BTCUSDT | 1h | 2026-01-05 13:45 | ⚠️ | 2026-01-05 15:00 | Rate limited |
☐ Filter by status: OK, WARNING, ERROR, NEVER_RUN
☐ Sorting by last run, next run, symbol
☐ Alerts:
  - "Red" if task has not run for >2x interval
  - "Yellow" if error in last 3 runs
  - "Green" if OK
☐ Email alert if red for >1 hour
☐ Optional webhook integration (Slack, Discord)
```

---

### 2.5 EPIC 5: Data Validation and Reconciliation (P1 - MVP)

#### **User Story 5.1: Data quality checks**
```
As a data quality officer
I want the platform to validate each candlestick
So that data integrity is guaranteed

Acceptance Criteria:
☐ Validation per candlestick:
  - high >= open, close, low (logical)
  - low <= open, close, high (logical)
  - high >= low (logical)
  - volume >= 0 (non-negative)
  - open_time < close_time (temporal)
  - time gap = expected interval (no duplicates/gaps)
☐ If validation fails: log in API_ERRORS, skip candlestick
☐ Count rejections, log in import_logs
☐ Alert if >5% rejections in a task
☐ Report: "Imported 989/1000, 11 rejected (time gaps)"
```

#### **User Story 5.2: Duplicate detection**
```
As a data engineer
I want the platform to detect and deduplicate
So that replicated data is avoided

Acceptance Criteria:
☐ Unique key: (table, open_time)
☐ Before insertion: select count(*) where open_time = X
☐ If exists: UPSERT option (update if exists)
☐ Comparison: exact OHLCV match?
  - If match: silently skip (thanks Binance for stability)
  - If different: log warning, take most recent version
☐ Duplicate logging: "Duplicate AXSUSDT 1h 2026-01-05 14:00, updated"
```

#### **User Story 5.3: Checksums and auditability**
```
As a compliance officer
I want each import to be verifiable
So that data integrity can be proven

Acceptance Criteria:
☐ Compute SHA256 of raw JSON received from Binance
☐ Store checksum in IMPORT_LOGS
☐ Query possible: "Verify import ID XYZ"
☐ Output: "Checksum valid ✅" or "Anomaly detected ❌"
☐ Export audit trail: [import_id, symbol, checksum, status]
```

---

### 2.6 EPIC 6: Alerting and Monitoring (P1 - MVP)

#### **User Story 6.1: Email notifications for critical errors**
```
As a trader
I want to receive an email alert if a task fails
So that I can react quickly to problems

Acceptance Criteria:
☐ Configuration: email, SMTP server
☐ Triggers:
  - HTTP 429 (rate limit exceeded)
  - HTTP 418 (IP ban)
  - HTTP 500+ (server error)
  - 0 candlesticks imported (probable error)
☐ Email template:
  Subject: "[CRITICAL] Cryptostory: AXSUSDT 1h failed"
  Body: "
  Task: AXSUSDT 1h
  Error: 429 Too Many Requests
  Time: 2026-01-05 14:32 UTC
  Retry: Automatic retry in 60s
  Action: Check rate limits
  "
☐ Debouncing: max 1 email per 5 minutes for same error
☐ Configurable: enable/disable per error type
```

---

## 3. AGILE ROADMAP (SPRINTS)

### 3.1 Two-week Sprint Planning (MVP Phase)

#### **SPRINT 1 (Weeks 1–2: Configuration + DB Foundation)**
**Objective**: Solid foundation for configuration and persistence

| User Story | Points | Priority | Assigned |
|-----------|--------|----------|----------|
| 1.1 - Basic TUI Configuration | 8 | P0 | Dev 1 |
| 1.2 - Dates + Timezone | 5 | P1 | Dev 2 |
| 2.1 - Table creation | 5 | P0 | Dev 1 |
| 2.2 - IMPORT_LOGS table | 3 | P1 | Dev 3 |

**Deliverables**: Complete TUI configuration, validated DB schema  
**Definition of Done**: Code review ✅, Unit tests ✅, Manual test ✅

#### **SPRINT 2 (Weeks 3–4: Binance API + Basic Fetch)**
**Objective**: Functional Binance API integration

| User Story | Points | Priority | Assigned |
|-----------|--------|----------|----------|
| 3.1 - uiKlines API | 8 | P0 | Dev 2 |
| 3.2 - Rate limit handling | 13 | P0 | Dev 1 |
| 2.3 - API_ERRORS table | 3 | P1 | Dev 3 |
| 1.3 - Limit parameter | 3 | P1 | Dev 2 |

**Deliverables**: Single-pair fetch successful, rate limits respected  
**Definition of Done**: Code review ✅, Unit tests ✅, Integration test ✅

#### **SPRINT 3 (Weeks 5–6: Chunking + Automation)**
**Objective**: Long-period data and task scheduling

| User Story | Points | Priority | Assigned |
|-----------|--------|----------|----------|
| 3.3 - Chunking | 13 | P0 | Dev 1 |
| 4.1 - Systemd/Cron generation | 8 | P0 | Dev 2 |
| 5.1 - Data validation | 5 | P1 | Dev 3 |
| 1.4 - CSV Import | 5 | P1 | Dev 2 |

**Deliverables**: Fetch 5+ years of data, scheduled runs working  
**Definition of Done**: Full integration test ✅, Manual 7-day test ✅

#### **SPRINT 4 (Weeks 7–8: Orchestration + Quality)**
**Objective**: Multi-pair orchestration, data quality

| User Story | Points | Priority | Assigned |
|-----------|--------|----------|----------|
| 4.2 - Multi-task orchestration | 13 | P0 | Dev 1 |
| 4.3 - Task monitoring dashboard | 8 | P0 | Dev 2 |
| 5.2 - Deduplication | 5 | P1 | Dev 3 |
| 6.1 - Email alerting | 8 | P1 | Dev 2 |

**Deliverables**: 50+ pairs running, monitoring dashboard, email alerts  
**Definition of Done**: 7-day stability test ✅, QA approved ✅

### 3.2 MVP Release (Week 9)
- Code freeze, bug fixes
- Final QA, security review
- Release v0.1-beta
- Documentation README

---

## 4. BUSINESS ACCEPTANCE CRITERIA

### 4.1 General Acceptance Criteria

For each user story, validation:

```
☐ Feature complete per description
☐ No blocking bugs identified
☐ Acceptable performance (<5s per operation)
☐ Detailed logging of each action
☐ Error handling with clear messages
☐ Tested code (unit + integration)
☐ User documentation present
☐ No broken dependencies
☐ Backward compatible if applicable
```

### 4.2 Infrastructure Acceptance Criteria

```
☐ Healthy database (no corruption)
☐ Binance rate limits respected (0 violations)
☐ Zero data loss on interruption
☐ Automatic recovery after error
☐ Structured and queryable logs
☐ Clear visual monitoring
```

### 4.3 User Acceptance Criteria

```
☐ MVP usable by non-developer persona
☐ Setup <10 minutes
☐ No Binance API expertise required
☐ Understandable error messages
☐ Sufficient documentation for self-service
```

---

## 5. DEPENDENCIES AND BLOCKERS

### 5.1 Identified Dependencies

| Dependency | Criticality | Owner | Resolution |
|-----------|-------------|-------|------------|
| Binance API account | P0 | Data Eng | Create test account, API keys |
| PostgreSQL + TimescaleDB stack | P0 | DevOps | Docker container, CI/CD |
| System architecture (Systemd vs Cron) | P0 | TA | Architecture decision |
| TUI Textual design | P0 | Frontend | Prototype wireframes |
| Binance API specifications | P0 | Data Eng | Already documented |

### 5.2 Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|-----|--------|-------------|------------|
| Binance API changes | Medium | Low | Monitor changelog, version pinning |
| Strict rate limits | Medium | Low | Flexible rate limit strategy |
| Slow DB performance | Medium | Medium | Index optimization, TimescaleDB tuning |
| Complex TUI | Medium | Medium | Early user testing |

---

## 6. SUCCESS METRICS

### 6.1 Product Metrics

| Metric | Target | Frequency |
|-------|--------|-----------|
| Installation success rate | >95% | Spot check |
| Time to first data import | <5 minutes | Post-release |
| Data import success rate | >99% | Daily |
| Task execution reliability | >99.5% | Daily |
| User satisfaction (NPS) | >50 | Monthly |

### 6.2 Technical Metrics

| Metric | Target | Frequency |
|-------|--------|-----------|
| Code coverage | >80% | Each build |
| Build time | <2 minutes | Each commit |
| Critical bugs found | 0 | Post-release |
| Performance (fetch 1000 rows) | <5s | Benchmark |

---

## 7. VALIDATION AND SIGN-OFF

**Backlog approved by:**

- Product Owner: _________________ Date: _______
- Stakeholders: _________________ Date: _______
- Technical Lead: _________________ Date: _______

**Roadmap accepted for Agile execution:** ✅

---

## APPENDIX A: GLOSSARY

- **UiKlines**: Binance endpoint for candlesticks (UI Klines)
- **Timeframe**: Time interval (1m, 1h, 1d, 1w, 1M)
- **Chunking**: Splitting a request into multiple sub-requests
- **Rate Limit**: Request limit per minute (Binance: 6000 weight/min)
- **Hypertable**: Time-partitioned table in TimescaleDB
- **Systemd Timer**: Modern Linux alternative to Cron
- **TUI**: Terminal User Interface (text-based interface)

---

## APPENDIX B: IMPACT MAP

```
User Stories
├── Configuration
│   ├── 1.1 TUI Basic
│   ├── 1.2 Dates + Timezone
│   ├── 1.3 Limit
│   └── 1.4 CSV Import
├── Data Persistence
│   ├── 2.1 Tables creation
│   ├── 2.2 Import logging
│   └── 2.3 Error tracking
├── Binance Integration
│   ├── 3.1 API fetch
│   ├── 3.2 Rate limits
│   └── 3.3 Chunking
├── Automation
│   ├── 4.1 Scheduler generation
│   ├── 4.2 Task orchestration
│   └── 4.3 Task monitoring
└── Quality
    ├── 5.1 Data validation
    ├── 5.2 Deduplication
    ├── 5.3 Checksums
    └── 6.1 Alerting
```
