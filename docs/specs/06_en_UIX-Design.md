# UIX - DESIGN SYSTEM AND USER INTERFACE
## Cryptostory Platform - TUI Design

**Document Version:** 1.0  
**Date:** January 2026  
**Status:** Approved  
**Audience:** Designers, Front-end Developers, QA

---

## 1. USER PERSONAS AND USER JOURNEYS

### 1.1 Detailed Personas

#### **Persona 1: Alex (Quant Trader)**
- **Profile**: 5+ years in algo trading, €500K+ AUM, tech-savvy
- **Goal**: Reliable access to historical data for multi-timeframe backtesting
- **Pain Points**: Binance rate limits, setup complexity, data loss
- **Journey**:
  1. Launch app → see TUI welcome
  2. Configure symbol (BTC/USDT), interval (1d, 1h, 1m), dates (5 years history)
  3. Click "Fetch Historical Data"
  4. See progress (chunking by 2.6M candlesticks)
  5. Auto-schedule daily updates
  6. Monitor dashboard (success ✅)
  
**Time**: 2–3 minutes from launch to running

#### **Persona 2: Jordan (Data Engineer)**
- **Profile**: 50-person FinTech startup, senior engineer
- **Goal**: Scalable infrastructure, proactive monitoring, zero manual intervention
- **Pain Points**: Hard monitoring, missing alerting, complex debugging
- **Journey** :
  1. Install via pip/Docker
  2. Set up DB + API keys
  3. Configure 100+ symbols (via CSV import)
  4. See Monitoring Dashboard (live status, errors, next runs)
  5. Receive Slack/email alerts on failures
  6. Sleep peacefully ✅

**Time**: 15–20 minutes setup, then automated

#### **Persona 3: Maya (Retail Trader)**
- **Profile**: Independent, personal portfolio, non-dev
- **Goal**: Simple, free, intuitive, no code
- **Pain Points**: API complexity, cloud costs, difficult setup
- **Journey** :
  1. Download + install
  2. Run app (TUI opens)
  3. Select BTC/USDT, 1h interval (from dropdowns)
  4. Click "Start" (defaults handle the rest)
  5. See data imported ✅
  6. Dashboard shows a new candlestick every hour

**Time**: <5 minutes to first data

#### **Persona 4: Prof. Chen (Researcher)**
- **Profile**: Academic, peer-reviewed publications, reproducibility is critical
- **Goal**: Reproducible data, easy export, open-source, certified
- **Pain Points**: Pro data costs, data ownership, reproducibility
- **Journey** :
  1. Clone GitHub repo (MIT license) ✅
  2. Run setup script (reproducible)
  3. Fetch data ETHUSDT 1d (2020–2026)
  4. Export CSV for paper
  5. Cite in references: "Cryptostory v1.0.2, timestamp checksum XXX" ✅

**Time**: 10 minutes to exportable data

---

## 2. UI ARCHITECTURE - SCREENS AND FLOWS

### 2.1 Screen Hierarchy

```
┌──────────────────────────────────────┐
│  WELCOME SCREEN (Startup)            │
│  ├─ [Setup New Symbol]               │
│  ├─ [Open Monitoring Dashboard]      │
│  └─ [View Settings]                  │
│                                      │
├─→ CONFIGURATION SCREEN              │
│   ├─ Asset selection (dropdown)     │
│   ├─ Quote selection (dropdown)     │
│   ├─ Interval selection (dropdown)  │
│   ├─ Date range (optional, picker)  │
│   ├─ Timezone (dropdown)            │
│   └─ [Confirm → Fetch]              │
│                                      │
├─→ PROGRESS SCREEN                   │
│   ├─ Progress bar (chunking visual) │
│   ├─ Rate limit status              │
│   └─ Real-time logs                 │
│                                      │
├─→ MONITORING DASHBOARD              │
│   ├─ Task status table              │
│   ├─ Metrics summary                │
│   ├─ Rate limit gauge               │
│   ├─ Recent errors                  │
│   └─ [Settings] [Alerts] [Export]   │
│                                      │
├─→ ALERTS SCREEN                     │
│   ├─ Error history                  │
│   ├─ Warnings                       │
│   └─ Notification preferences       │
│                                      │
└─→ SETTINGS SCREEN                   │
    ├─ DB connection                  │
    ├─ Email alerts config            │
    ├─ Data retention                 │
    └─ [Save] [Reset to Default]      │
```

---

## 3. DETAILED SCREEN DESIGNS

### 3.1 Welcome Screen

```
╔═══════════════════════════════════════════════════════════════╗
║  🚀 CRYPTOSTORY v1.0.2                                        ║
║     Market Data Collection Platform                           ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌─────────────────────────────────────────────────────────┐  ║
║  │                                                         │  ║
║  │  Status: ✅ All Systems Operational                      │  ║
║  │                                                         │  ║
║  │  Database: Connected (cryptostory)                       │  ║
║  │  Binance API: Accessible (Rate: 1200/6000)               │  ║
║  │  Last Import: 2026-01-05 14:45:32 UTC (BTCUSDT 1h)        │  ║
║  │                                                         │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  QUICK ACTIONS:                                               ║
║                                                               ║
║  [ ➕ Setup New Symbol ] [ 📊 Monitoring Dashboard ]          ║
║  [ ⚙️  Settings ]         [ 📋 View Logs ]                    ║
║                                                               ║
║  CONFIGURED SYMBOLS: 23                                       ║
║                                                               ║
║  Symbol        Interval  Status  Last Run      Next Run       ║
║  ──────────────────────────────────────────────────────────   ║
║  BTCUSDT       1h        ✅      14:45:32      15:45:32       ║
║  ETHUSDT       1h        ✅      14:45:45      15:45:45       ║
║  ADAUSDT       1h        ⚠️      14:43:12      15:43:12 (late) ║
║  BNBUSDT       1d        ✅      00:00:02      ─ (today)       ║
║                                                               ║
║  Press [1] for Setup | [2] for Dashboard | [3] for Settings   ║
║  Press [q] to Quit                                            ║
╚═══════════════════════════════════════════════════════════════╝
```

**Interactions**:
- [1] → Go to Configuration Screen
- [2] → Go to Monitoring Dashboard
- [3] → Go to Settings
- [q] → Exit app (confirm prompt)
- [↓] / [↑] → Scroll symbol list

---

### 3.2 Configuration Screen (Detailed)

```
╔═══════════════════════════════════════════════════════════════╗
║  SET UP NEW DATA COLLECTION                                   ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  STEP 1/6 : Select Asset                                      ║
║  ───────────────────────────────────────────────────────────  ║
║  Which cryptocurrency would you like to fetch?                ║
║                                                               ║
║  Asset: ┌─────────────────────────────────────────────────┐   ║
║         │ BTC ▼ (Bitcoin)                                  │   ║
║         │                                                  │   ║
║         │ Recent: ADA, BNB, XRP                            │   ║
║         │                                                  │   ║
║         │ All Assets (type to search):                     │   ║
║         │  • ADA - Cardano                                 │   ║
║         │  • MATIC - Polygon                               │   ║
║         │  • BTC - Bitcoin                                 │   ║
║         │  • SOL - Solana                                  │   ║
║         │  ...more (100+)                                  │   ║
║         └─────────────────────────────────────────────────┘   ║
║                                                               ║
║  STEP 2/6 : Select Quote Currency                             ║
║  ───────────────────────────────────────────────────────────  ║
║  Quote: ┌─────────────────────────────────────────────────┐   ║
║         │ USDT ▼ (Tether - Recommended)                    │   ║
║         │  • USDT (most liquidity)                         │   ║
║         │  • USDC (stable)                                 │   ║
║         │  • EUR (euro)                                    │   ║
║         │  • BUSD (Binance USD)                            │   ║
║         └─────────────────────────────────────────────────┘   ║
║                                                               ║
║  ✅ Complete Symbol: BTCUSDT                                  ║
║  ✅ Binance Pair Status: Available (since 2017-01-01)         ║
║                                                               ║
║  [← Back] [Next →]                                            ║
║  [TAB = Next field] [SHIFT+TAB = Previous] [ESC = Cancel]     ║
╚═══════════════════════════════════════════════════════════════╝
```

**Key Features**:
- Searchable dropdown (type to filter)
- Real-time symbol validation ✅/❌
- Recent assets shown first
- Preview of complete symbol
- Info: pair existence + history start date

---

### 3.3 Monitoring Dashboard (Main)

```
╔═══════════════════════════════════════════════════════════════╗
║  📊 MONITORING DASHBOARD (Auto-refresh: 30s)                  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  SUMMARY METRICS:                                             ║
║  ───────────────────────────────────────────────────────────  ║
║  Total Tasks: 23      Running: 2     Queued: 3    Completed:18 ║
║  Success Rate: 99.5%  (Last 24h)                              ║
║  Data Imported: 45.2K candlesticks (24h)                      ║
║  Rate Limit Usage: 2450/6000 (40.8%) | Reset: 45 min          ║
║                                                               ║
║  ACTIVE TASKS:                                                ║
║  ───────────────────────────────────────────────────────────  ║
║  Symbol      │ Interval │ Status │ Last Run    │ Next Run      ║
║  ─────────────┼──────────┼────────┼─────────────┼────────────  ║
║  BTCUSDT    │ 1h       │ ✅     │ 14:45:32   │ 15:45:32       ║
║  ETHUSDT    │ 1h       │ 🔄     │ 14:50:12   │ 15:50:12       ║
║  ADAUSDT    │ 1h       │ ⚠️     │ 14:43:12   │ 15:43:12       ║
║  BNBUSDT    │ 1d       │ ✅     │ 00:00:02   │ 2026-01-06     ║
║  XRPUSDT    │ 1m       │ ✅     │ 14:52:15   │ 14:53:15       ║
║  LTCUSDT    │ 1w       │ ✅     │ 2026-01-03 │ 2026-01-10     ║
║  DOGUSDT    │ 1M       │ ✅     │ 2025-12-01 │ 2026-02-01     ║
║                                                               ║
║  ✅ = Success  🔄 = Running  ⚠️  = Warning  ❌ = Error         ║
║                                                               ║
║  STATUS LEGEND:                                               ║
║  • Green (✅): Last 3 runs successful                         ║
║  • Yellow (⚠️): 1 error in last 3 runs, recovering            ║
║  • Red (❌): Failed, needs investigation                      ║
║                                                               ║
║  RECENT ERRORS (Last 5):                                      ║
║  ───────────────────────────────────────────────────────────  ║
║  2026-01-05 14:43 | ADAUSDT 1h | Error 429: Rate limited      ║
║  2026-01-05 13:22 | XRPUSDT 1m | Timeout (retrying...)        ║
║                                                               ║
║  [🔄 Refresh Now] [⚙️  Settings] [📧 Alerts] [📥 Export]      ║
║  Use ↑↓ to scroll | [f] Filter | [s] Sort | [q] Quit          ║
╚═══════════════════════════════════════════════════════════════╝
```

**Interactivity**:
- Auto-refresh every 30s (configurable)
- Filter by status: [f] → filter dialog
- Sort: [s] → sort by (last run, interval, status)
- Color coding:
  - ✅ Green = OK
  - ⚠️ Yellow = Warning (1 error)
  - ❌ Red = Error (needs attention)
- Hover to see full details
- Click to see a task’s history

---

### 3.4 Alerts Screen

```
╔═══════════════════════════════════════════════════════════════╗
║  🚨 ALERTS & ERRORS                                           ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ERROR SUMMARY:                                               ║
║  ───────────────────────────────────────────────────────────  ║
║  Total Errors (24h): 5                                        ║
║  • 429 (Rate limited): 2                                      ║
║  • Timeout: 2                                                 ║
║  • Validation failed: 1                                       ║
║                                                               ║
║  RECENT ERROR LOG:                                            ║
║  ───────────────────────────────────────────────────────────  ║
║  Timestamp        │ Symbol   │ Error                          ║
║  ─────────────────┼──────────┼─────────────────────────────── ║
║  2026-01-05 14:43│ ADAUSDT  │ 429: Too many requests          ║
║                  │ (1h)     │ Retry in 60s... ✓ Success       ║
║  ─────────────────┼──────────┼─────────────────────────────── ║
║  2026-01-05 13:22│ XRPUSDT  │ Timeout after 10s               ║
║                  │ (1m)     │ Retrying... ✓ Success           ║
║  ─────────────────┼──────────┼─────────────────────────────── ║
║  2026-01-05 12:01│ DGEUSDC  │ 404: Symbol not found           ║
║                  │ (1d)     │ ❌ Skip DGEUSDC pair             ║
║                                                               ║
║  ALERT NOTIFICATIONS:                                         ║
║  ───────────────────────────────────────────────────────────  ║
║  Email Alerts:                                                ║
║  ☑️  On critical error (IP ban, persistent failure)           ║
║  ☑️  Daily summary (if any errors)                            ║
║  ☐  Rate limit approaching 80%                                ║
║                                                               ║
║  Webhook (Slack/Discord): [⚙️  Configure]                     ║
║  ☑️  Enable Slack notifications                               ║
║  Webhook URL: https://hooks.slack.com/... [✏️  Edit]          ║
║                                                               ║
║  [📧 Send Test Alert] [🗑️  Clear History] [⚙️  Settings]      ║
║  [q] Back to Dashboard                                        ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 4. DESIGN SYSTEM & COMPONENTS

### 4.1 Color Palette (Terminal-optimized)

```
Primary Colors:
  ✅ Success / OK:         Green   (#22C55E)
  ⚠️  Warning / Caution:   Yellow  (#EAB308)
  ❌ Error / Critical:     Red     (#EF4444)
  ℹ️  Info / Default:      Blue    (#3B82F6)
  
Neutral:
  Background:  Dark Gray  (#1F2937)
  Text:        Light Gray (#E5E7EB)
  Borders:     Medium     (#6B7280)
  Accent:      Cyan       (#22C55E) - Primary accent
  
Status Indicators:
  Running (🔄):  Cyan
  Pending (⏳):  Yellow
  Done (✅):     Green
  Failed (❌):   Red
```

### 4.2 Typography & Spacing

```
Headers:
  H1: Bold, 20px, Top padding 2
  H2: Bold, 16px, Top padding 1
  H3: Semi-bold, 14px
  
Body:
  Default: Regular, 14px
  Monospace: 12px (for timestamps, data)
  
Spacing:
  Margin: 1 line (top), 1 line (bottom)
  Padding: 1 space (left), 1 space (right)
  Column gap: 3 spaces (for alignment)
```

### 4.3 Interactive Components

#### Button Component
```
Appearance:
  [ Click me ]  (standard)
  [✓ Confirm] (action required)
  [← Back]     (navigation)
  
Focus state:
  [> Click me <]  (inversed colors)
  
Disabled:
  [Click me]  (grayed out)
```

#### Input Component
```
Text Input:
  Label: ______________________
  [user input here, cursor _]
  
Dropdown:
  Selection: Option 1 ▼
  
  Option 1 ← selected
  Option 2
  Option 3

Checkbox:
  ☑️  Enable notifications
  ☐  Disabled option
```

#### Table Component
```
┌─────────┬──────────┬────────┬──────────┐
│ Column1 │ Column 2 │ Status │ Action   │
├─────────┼──────────┼────────┼──────────┤
│ Value A │ Value B  │ ✅ OK  │ [Edit]   │
│ Value C │ Value D  │ ⚠️ Warn│ [Delete] │
└─────────┴──────────┴────────┴──────────┘
```

---

## 5. USER FLOWS & INTERACTIONS

### 5.1 First-Time User Flow

```
1. Launch App
   ↓
2. See Welcome Screen
   ├─ Status indicators (DB OK, Binance OK)
   └─ Quick actions buttons
   ↓
3. Click [Setup New Symbol]
   ↓
4. Configuration Wizard (6 steps)
   ├─ Step 1: Asset selection
   ├─ Step 2: Quote currency
   ├─ Step 3: Interval selection
   ├─ Step 4: Date range (optional)
   ├─ Step 5: Timezone (optional)
   └─ Step 6: Review & confirm
   ↓
5. Click [Fetch & Schedule]
   ↓
6. See Progress Screen
   ├─ Progress bar (chunking)
   ├─ Rate limit usage
   └─ Real-time logs
   ↓
7. Success notification
   ├─ "Data imported: 1000 candlesticks ✅"
   ├─ "Scheduled: Daily at 00:00 UTC"
   └─ [View Dashboard]
   ↓
8. Automated from here on
   └─ Daily updates happen automatically
```

**Time to Value**: 3–5 minutes from launch to first data

---

### 5.2 Regular Usage Flow

```
1. User launches app
   ↓
2. Welcome screen shows status
   ├─ All tasks: ✅ (or ⚠️ if errors)
   └─ Quick glance at next runs
   ↓
3. User navigates to Dashboard
   ├─ Sees all configured symbols
   ├─ Status of each task
   └─ Next scheduled runs
   ↓
4. If errors detected:
   ├─ Go to Alerts screen
   ├─ See error details
   └─ Auto-recovery in progress (or manual action needed)
   ↓
5. Normal operation:
   └─ Nothing to do! Automated.
```

---

## 6. ACCESSIBILITY & UX BEST PRACTICES

### 6.1 Keyboard Navigation

```
Tab Key Navigation:
  • Move to next field/button
  • Shift+Tab = move backwards
  
Arrow Keys:
  • ↑/↓ = navigate lists
  • ←/→ = switch tabs
  
Shortcuts:
  • [q] = Quit current screen
  • [?] = Help
  • [Ctrl+C] = Force quit
  • [Space] = Toggle checkbox
  • [Enter] = Confirm/Submit
```

### 6.2 Accessibility Features

```
Visual:
  ✅ High contrast (light text on dark)
  ✅ Color + symbols (not color alone)
  ✅ Large text (terminal default)
  ✅ Clear focus indicators
  
Motor:
  ✅ Full keyboard navigation
  ✅ No time limits on input
  ✅ Large clickable areas (terminal lines)
  
Cognitive:
  ✅ Consistent layout
  ✅ Clear error messages
  ✅ Confirmations for destructive actions
  ✅ Help text available [?]
```

### 6.3 Error Messages (Clear & Actionable)

```
❌ Bad: "Error occurred"
✅ Good: "Error 429: Rate limit exceeded
         Retrying in 60 seconds...
         To speed up, reduce concurrent tasks."

❌ Bad: "DB connection failed"
✅ Good: "Database connection failed to localhost:5432
         Check:
         1. PostgreSQL service running? (systemctl status postgresql)
         2. Connection string in settings.yaml correct?
         3. Credentials have permission?"
```

---

## 7. PROTOTYPES & MOCKUPS

### 7.1 Low-Fidelity Wireframe Example

```
Configuration Screen Structure:
┌─────────────────────────────────────┐
│ Header: Step 1/6                    │
├─────────────────────────────────────┤
│ Label: "Select Asset"               │
│ Dropdown: [BTC ▼ ]                  │
│                                     │
│ Label: "Quote Currency"             │
│ Dropdown: [USDT ▼]                  │
│                                     │
│ Info: "Symbol: BTCUSDT ✅"          │
│                                     │
│ Footer: [Back] [Next]               │
└─────────────────────────────────────┘
```

### 7.2 Interactive Prototype

The full interactive prototype is available in Textual:
- Run: `python -m cryptostory.tui`
- Live CSS editor: `textual run --dev`
- Test on multiple terminal widths

---

## 8. RESPONSIVE DESIGN

### 8.1 Different Terminal Sizes

```
Small (80x24):
┌────────────────────────────┐
│ CRYPTOSTORY (Compact)      │
├────────────────────────────┤
│ BTC 1h ✅ 14:45            │
│ ETH 1h ✅ 14:50            │
│ ...                        │
│ [Setup] [Monitor] [Quit]   │
└────────────────────────────┘

Medium (120x30):
┌──────────────────────────────────────────────┐
│ CRYPTOSTORY - Monitoring Dashboard           │
├──────────────────────────────────────────────┤
│ Symbol   │ Interval │ Status │ Last Run      │
│ BTCUSDT  │ 1h       │ ✅     │ 14:45:32      │
│ ETHUSDT  │ 1h       │ ✅     │ 14:50:12      │
│ [Setup] [Settings] [Alerts] [Export]         │
└──────────────────────────────────────────────┘

Large (200x50):
  (Full dashboard with detailed metrics, graphs, etc.)
```

---

## 9. TESTING & VALIDATION

### 9.1 User Testing Plan

```
Phase 1: Moderated Testing (Week 2)
  • 3 users: 1 quant, 1 non-technical, 1 data engineer
  • Scenarios: Setup, monitor, error handling
  • Feedback: UX flows, error clarity, navigation

Phase 2: Unmoderated Testing (Week 3)
  • 10 early users (beta)
  • Metrics: Time to setup, error rates, satisfaction
  • Surveys: NPS, pain points, desired features

Phase 3: Beta Release (Week 4)
  • Open beta, community feedback
  • Iterate on top issues
```

### 9.2 Acceptance Criteria

```
☐ All screens render correctly at 80x24 minimum
☐ Navigation works with keyboard only (no mouse)
☐ Error messages are clear and actionable
☐ Progress bars show actual progress (not frozen)
☐ Colors distinguishable in both light/dark terminals
☐ Response time < 100ms for user interactions
☐ Help text available via [?] on all screens
☐ Consistency of layout across all screens
```

---

## 10. FUTURE UI ENHANCEMENTS

### 10.1 Phase 2 (Q2 2026)

```
- Web Dashboard (complementary to TUI)
- Data Export UI (CSV, Parquet downloads)
- Analytics Charts (success rates, data volume)
- Mobile companion app (alerts, status check)
```

### 10.2 Phase 3 (Q3 2026)

```
- Advanced filtering/search in monitoring
- Custom alerts configuration UI
- Data visualization (candlestick charts in TUI?)
- Performance profiling dashboard
```

---

## CONCLUSION

This design is intended to be:
- **Intuitive**: Non-technical users can configure in <5 minutes
- **Powerful**: Data engineers have full visibility and control
- **Responsive**: Works on all terminals (80x24 and up)
- **Accessible**: Full keyboard navigation
- **Beautiful**: Modern TUI without unnecessary complexity

**Approved by:** UI/UX Designer _________________ Date: _______

---

## APPENDIX A: DESIGN TOKENS (CSS)

```css
/* Colors */
--color-success: #22C55E;
--color-warning: #EAB308;
--color-error: #EF4444;
--color-info: #3B82F6;
--color-bg: #1F2937;
--color-text: #E5E7EB;
--color-border: #6B7280;

/* Spacing */
--space-xs: 1px;
--space-sm: 1 line;
--space-md: 2 lines;
--space-lg: 3 lines;

/* Typography */
--font-size-xs: 11px;
--font-size-sm: 12px;
--font-size-base: 14px;
--font-size-lg: 16px;
--font--weight-normal: 400;
--font-weight-bold: 700;
```

---

## APPENDIX B: STYLE GUIDE

### Button Styles
- Standard: `[Text]` - clickable region with brackets
- Focused: `[> Text <]` - inverse colors, centered arrow
- Disabled: `[Text]` - grayed out, not clickable

### Table Styles
- Header row: bold, with borders `├─┼─┤`
- Data rows: regular text
- Alternating rows: optional lighter shade every 2nd row
- Column alignment: left for text, right for numbers

### Form Styles
- Labels: Bold, above field
- Required: ` *` after label
- Error: Red text below field
- Help: Light gray text, below field

:contentReference[oaicite:0]{index=0}
