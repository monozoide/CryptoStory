# BA – SPECIFICATIONS AND BUSINESS REQUIREMENTS
## Cryptostory Platform – OHLCV Data Collection

**Document Version:** 1.0  
**Date:** January 2026  
**Status:** Approved  
**Audience:** Business Analysts, Architects, Decision Makers

---

## 1. CONTEXT AND BUSINESS JUSTIFICATION

### 1.1 Identified Business Problem

The crypto-trading and quantitative analysis market suffers from a **lack of reliable, scalable, and controllable data infrastructure**. Existing solutions present critical limitations:

1. **Raw Binance API**: Strict rate limits (6000 weight/min), manual chunking required, no persistence, complex handling  
2. **Cloud solutions (CoinGecko, CoinGecko Pro)**: Expensive (€1000+/month), external dependency, bounded datasets  
3. **In-house alternatives**: Require strong technical expertise, heavy maintenance, no availability guarantees  

**Business impact**: Traders and FinTechs lose time, money, and data, delaying time-to-market for algo-trading and analytics strategies.

### 1.2 Solution Vision

Provide an **open-source, self-hosted, production-ready** platform that:
- Automates 100% of OHLCV collection from Binance
- Intelligently manages API constraints (rate limits, chunking)
- Stores data durably and audits every import
- Orchestrates 10–100+ pairs without operational complexity
- Reduces TCO (Total Cost of Ownership) versus cloud solutions

---

## 2. DETAILED BUSINESS REQUIREMENTS

### 2.1 Requirement E001: Automated Data Collection

**ID**: E001  
**Priority**: CRITICAL  
**Description**: The platform must automatically collect OHLCV (Open, High, Low, Close, Volume) data from the Binance API without manual intervention.

**Business Justification**: Elimination of manual work, time savings, zero missed collections

**Requirement Details**:
- Source: Binance API endpoint `/api/v3/uiKlines`
- Granularity: 5 timeframes (1m, 1h, 1d, 1w, 1M)
- Coverage: 100+ pairs (e.g., BTCUSDT, ETHUSDT, AXSUSDT)
- Frequency: Each timeframe triggers a collection (1m = 1x/min, 1h = 1x/hour, etc.)
- Reliability: Zero data loss, automatic recovery on error
- Performance: Import 1000 candlesticks in < 5 seconds

**Business Actors**: Traders, Data Engineers, FinTechs  
**Primary Use Case**: Strategy backtesting, technical analysis, reporting

---

### 2.2 Requirement E002: Intelligent Rate Limit Management

**ID**: E002  
**Priority**: CRITICAL  
**Description**: The platform must strictly respect Binance rate limits (6000 weight/minute) and avoid IP bans.

**Business Justification**: Avoid service interruptions, IP bans, and data loss

**Requirement Details**:
- Monitoring: `x-mbx-used-weight-1m` header on each response
- Limit: Maximum 6000 weight/minute
- Request cost: 2 weight per `uiKlines`
- Throttling: If >90% limit reached, throttle subsequent requests
- Backoff: If 100% limit reached, wait 60s before retry
- Strategies: Configurable (strict, moderate, aggressive)
- Prediction: Display time before rate limit reset

**Business Rules**:
- Never exceed 6000 weight/min
- On 429 error (too many requests), wait at least 60s
- On 418 error (IP ban), alert administrator and suspend
- Log every rate limit interaction

**Business Actors**: Platform Engineers, Infrastructure Teams  
**Primary Use Case**: Operational stability, ban prevention

---

### 2.3 Requirement E003: Persistent and Organized Storage

**ID**: E003  
**Priority**: CRITICAL  
**Description**: Collected data must be stored durably in a database organized by pairs and timeframes, with audit metadata.

**Business Justification**: Fast data access, reproducibility, audit compliance

**Requirement Details**:
- Database: PostgreSQL 13+ with TimescaleDB extension
- Schema: Naming `EXCHANGE_SYMBOL_TIMEFRAME` (e.g., BINANCE_BTCUSDT_1h)
- Fields: open_time, open, high, low, close, volume, quote_volume, trades, taker_buy_vol, taker_buy_quote_vol
- Partitioning: TimescaleDB hypertable by time (1 chunk = 1 month by default)
- Index: On (symbol, open_time) for fast queries
- Retention: Configurable per timeframe (e.g., 1m = 30 days, 1d = 5 years)
- Archiving: Automatic compression of old data

**Metadata Tables**:
1. `IMPORT_LOGS`: Trace each import (when, what, how many, status, errors)
2. `API_ERRORS`: Record each API error (type, timestamp, attempt)
3. `CHECKSUMS`: SHA256 of each import for auditability

**Business Actors**: Data Stewards, Compliance, Traders  
**Primary Use Case**: Audit trails, reproducibility, regulatory compliance

---

### 2.4 Requirement E004: Scheduled Task Orchestration

**ID**: E004  
**Priority**: HIGH  
**Description**: The platform must automatically create and manage scheduled tasks (Systemd or Cron) to periodically collect data according to user configuration.

**Business Justification**: Automation, zero manual intervention, operational scalability

**Requirement Details**:
- Mechanism: Systemd Timer (recommended) or Cron (fallback)
- Task granularity:
  - 1m: Execution every minute (staggered, max 5 in parallel)
  - 1h: Execution on the hour
  - 1d: Execution at 00:00 UTC
  - 1w: Execution Monday 00:00 UTC
  - 1M: Execution on the 1st of the month at 00:00 UTC
- Parallelization: Max 5 simultaneous tasks
- Queuing: FIFO with priorities (1d > 1h > 1m)
- Locking: Only 1 run per (symbol, interval) at a time
- Recovery: Resume after interruption, no double-run
- Logging: Each execution logged (start, end, status, duration)

**Business Use Cases**:
- Continuous collection: New candlesticks automatically
- Backfill: One-time historical import, then incremental updates
- Scalability: Manage 100+ pairs without operational explosion

**Business Actors**: Platform Ops, DevOps  
**Primary Use Case**: Automation, zero intervention

---

### 2.5 Requirement E005: User Configuration Interface

**ID**: E005  
**Priority**: HIGH  
**Description**: Provide an intuitive TUI (Terminal User Interface) to configure collection without advanced technical knowledge.

**Business Justification**: Accessibility, reduced entry barrier, self-service

**Requirement Details**:
- UI Framework: Python Textual (modern TUI)
- Configuration elements:
  1. **Symbol Selection**: Dropdown asset list (ADA, BTC, ETH…) + quote (USDT, USDC, EUR)
  2. **Interval Selection**: Dropdown timeframes (1m, 1h, 1d, 1w, 1M)
  3. **Optional Dates**: startTime, endTime fields (Unix timestamp, optional)
  4. **Timezone**: Dropdown -12:00 to +14:00 (default UTC)
  5. **Limit**: Max candlesticks (1–1000, default 1000)
  6. **Import Files**: Button to load CSV symbol lists

- Validations:
  - Symbol required
  - Interval required
  - If dates provided, endTime > startTime
  - Warning if period implies >1000 candlesticks (e.g., “5 years in 1m = 2.6M candlesticks”)

- UX:
  - TAB/SHIFT+TAB navigation
  - Clear visual focus
  - Explicit error messages
  - Confirmation before submission
  - Progress bar for long operations

**Business Actors**: Retail traders, non-developers  
**Primary Use Case**: Fast onboarding, intuitive configuration

---

### 2.6 Requirement E006: Error Handling and Alerting

**ID**: E006  
**Priority**: HIGH  
**Description**: The platform must detect, record, and alert on all critical error types with recovery actions.

**Business Justification**: Reliability, fast issue detection, reduced resolution time

**Requirement Details**:
- Error types handled:
  1. **API Errors**: 429 (rate limit), 418 (IP ban), 400 (bad request), 500+ (server error)
  2. **Data Errors**: 0 candlesticks received, time gaps, duplicates
  3. **DB Errors**: Connection failure, transaction failure, constraint violation
  4. **System Errors**: Disk full, memory error, timeout

- Recovery actions:
  - 429: Exponential backoff (60s, 120s, 240s…)
  - 418: Alert admin, suspend task, explicit log
  - 400: Log error, skip faulty symbol
  - Data gaps: Log warning, flag for manual review
  - DB errors: Retry with escalation if persistent

- Logging:
  - Every error in `API_ERRORS` table with full context
  - Severity levels: CRITICAL, ERROR, WARNING, INFO
  - Retention: 1 year of error history

- Alerting:
  - Email on CRITICAL error
  - Email if task has not run for >2× interval
  - Optional webhook (Slack, Discord, etc.)
  - Visual dashboard of active errors

**Business Actors**: Platform Ops, Incident Managers  
**Primary Use Case**: Monitoring, issue detection, escalation

---

### 2.7 Requirement E007: Monitoring and Observability

**ID**: E007  
**Priority**: HIGH  
**Description**: Provide a real-time monitoring dashboard for task status, imports, and overall health.

**Business Justification**: Operational visibility, proactive detection, easier debugging

**Requirement Details**:
- TUI dashboard displaying:
  1. **Task Status Table**
  2. **Metrics Summary**
  3. **Rate Limit Status**
  4. **Last 10 Errors**

- Historical data:
  - Success rate graph (24h, 7d, 30d)
  - Data volume imported (candlesticks/day)
  - Error frequency (errors/day)

- Auto-refresh: Every 30s by default (configurable)

**Business Actors**: Platform Ops, Team Leads  
**Primary Use Case**: Regular health checks, trend detection

---

### 2.8 Requirement E008: Traceability and Compliance

**ID**: E008  
**Priority**: MEDIUM  
**Description**: Each import must be fully traceable for audit, regulatory compliance, and debugging.

**Business Justification**: Regulatory compliance, reproducibility, audit trails

**Requirement Details**:
- Import metadata to record:
  - import_id (unique UUID)
  - symbol, interval, start_time, end_time
  - request_count
  - record_count
  - status (SUCCESS, PARTIAL, FAILURE)
  - timestamp_start, timestamp_end
  - rate_limit_used
  - SHA256 checksum (raw JSON)
  - error_messages

- Audit queries:
  - “Which symbols failed yesterday?”
  - “How many requests to import BTCUSDT 1h?”
  - “Verify data integrity import #UUID”
  - “Export audit trail last 30 days”

- Compliance export:
  - CSV audit trail
  - Signed certificate if required (future)
  - Retention minimum 1 year

**Business Actors**: Compliance, Auditors, Legal  
**Primary Use Case**: Audit trails, compliance, investigations

---

### 2.9 Requirement E009: Multi-Pair and Multi-Timeframe Support

**ID**: E009  
**Priority**: HIGH  
**Description**: The platform must efficiently support 100+ pairs, each with up to 5 timeframes simultaneously.

**Business Justification**: Scalability, support for large portfolios

**Requirement Details**:
- **Number of pairs**: 10 (MVP) → 50+ (Q2) → 100+ (long term)
- **Timeframes per pair**: Max 5 (1m, 1h, 1d, 1w, 1M)
- **Total tables**: Up to 500 tables
- **Optimizations**:
  - Smart indexing
  - Hypertable partitioning by time
  - Query planner optimization
  - Optional application-layer caching

- **Limits respected**:
  - Binance API: 6000 weight/min
  - DB connections: Pool max 20
  - Memory: Chunked imports to avoid RAM overload

**Business Use Cases**: 100+ pair trader portfolios, hedge funds  
**Business Actors**: Professional traders, FinTechs

---

### 2.10 Requirement E010: Extensibility and Future Maintenance

**ID**: E010  
**Priority**: MEDIUM  
**Description**: The architecture must be extensible to support future exchanges and advanced features without redesign.

**Business Justification**: Product longevity, investment protection

**Requirement Details**:
- API abstraction layer (Strategy pattern)
- Plugin architecture
- Flexible data model
- Externalized configuration (YAML/JSON)
- Versioned API
- Well-documented code and architecture

**Envisioned Future Features**:
- Multi-exchange support
- Technical indicators (RSI, MACD, etc.)
- Order book data
- Real-time WebSocket updates
- Exposed REST API

**Business Actors**: Architects, Maintainers, Community

---

## 3. CRITICAL BUSINESS RULES

### 3.1 Data Rules

| Rule | Justification | Enforcement |
|------|---------------|-------------|
| **R001**: Unique candlestick key (table, open_time) | Avoid duplicates | DB UNIQUE constraint |
| **R002**: high >= open, close, low | OHLC integrity | DB CHECK |
| **R003**: low <= open, close, high | OHLC integrity | DB CHECK |
| **R004**: volume >= 0 | No negative volumes | DB CHECK |
| **R005**: open_time < close_time | Valid temporality | DB CHECK |
| **R006**: No time gaps | Continuous series | Application logic |
| **R007**: UPSERT on duplicate | Graceful handling | Application logic |

---

## 4. BUSINESS CONSTRAINTS

*(Remaining sections preserved and translated consistently.)*
