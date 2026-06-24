# Claude Profile Stats TRD

## Document Status

- Status: Draft v0
- Date: 2026-06-24
- Owner: Subin
- Related: [PRD.md](./PRD.md)
- Notes: This technical requirements document is an implementation-oriented draft and will likely evolve during development.

## 1. Technical Summary

Claude Profile Stats will be a local-first static asset generation tool. It will ingest Claude local usage data, persist aggregate history in SQLite, derive product metrics, generate SVG outputs, and optionally publish those outputs into a GitHub profile repository.

The technical design explicitly avoids depending on a hosted backend for MVP.

## 2. High-Level Architecture

The system will have four main layers:

1. Collector
2. Store
3. Renderer
4. Publisher

### Collector

Responsibilities:

- Discover Claude local session files
- Parse session usage metadata
- Normalize extracted records
- Detect new or changed sessions

### Store

Responsibilities:

- Persist session-level ingested summaries
- Persist daily rollups
- Persist future quota snapshots and events
- Provide deterministic query surfaces for rendering

### Renderer

Responsibilities:

- Read derived metrics from the database
- Generate static SVG assets
- Generate `profile-summary.json`

### Publisher

Responsibilities:

- Copy generated outputs into a GitHub profile repo
- Prepare files for commit

## 3. Recommended Tech Stack

### Language

Python is recommended for MVP because:

- Claude local parsing logic is straightforward in Python
- SQLite access is simple
- SVG templating can be done cleanly with string templates or Jinja2
- A single-language local tool keeps complexity low

### Storage

- SQLite for persistent local storage

### Config

- TOML config file

### Output

- SVG for profile assets
- JSON for summary export

## 4. Repository Strategy

This project should be built as a new repository rather than as an extension of the previously reviewed dashboard repository.

Reasoning:

- The target product is not a session browser
- The core need is long-lived rollups plus static profile assets
- A lighter architecture is preferable to adapting a larger FastAPI + frontend codebase

The previous repository remains useful as reference for:

- Claude local file layout assumptions
- usage field parsing approach
- cost estimation logic inspiration

## 5. Proposed Project Structure

```text
claude-profile-stats/
  src/
    app.py
    collector/
      sessions.py
      quota.py
    store/
      db.py
      schema.py
      queries.py
      rollups.py
    renderer/
      badges.py
      money.py
      grass.py
      summary.py
      templates/
    publisher/
      profile_repo.py
    common/
      config.py
      paths.py
      time.py
      types.py
  data/
    profile.db
  output/
    claude-badges.svg
    money-copy-card.svg
    claude-grass.svg
    profile-summary.json
  config.toml
  README.md
```

## 6. CLI / Workflow Design

### Primary Commands

```bash
python -m src.app sync
python -m src.app render
python -m src.app publish
```

### `sync`

Responsibilities:

- scan Claude local data
- ingest sessions
- update daily rollups
- update derived metrics and achievements

### `render`

Responsibilities:

- generate all SVG assets
- generate summary JSON

### `publish`

Responsibilities:

- copy output assets into configured GitHub profile repo path

### Optional Convenience Command

```bash
python -m src.app all
```

This would execute:

1. sync
2. render
3. publish

## 7. Source Data Model

### Session Data Source

Primary source:

- Claude local session JSONL files under configured Claude base path

Expected extracted fields:

- session UUID
- timestamp range
- usage totals
- model identifiers
- project path
- optional derived git identity

### Quota Data Source

Deferred for initial MVP.

Planned future source:

- locally observable quota or usage-limit state snapshots

## 8. Database Design

### 8.1 `sessions_ingested`

Purpose:

- durable record of already-processed sessions
- protects against duplicate ingestion

Suggested schema:

```sql
CREATE TABLE sessions_ingested (
  session_uuid TEXT PRIMARY KEY,
  jsonl_path TEXT NOT NULL,
  source_mtime REAL,
  first_seen_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  session_start_at TEXT,
  session_end_at TEXT,
  session_date TEXT NOT NULL,
  input_tokens INTEGER NOT NULL DEFAULT 0,
  output_tokens INTEGER NOT NULL DEFAULT 0,
  cache_creation_tokens INTEGER NOT NULL DEFAULT 0,
  cache_read_tokens INTEGER NOT NULL DEFAULT 0,
  estimated_cost_usd REAL NOT NULL DEFAULT 0,
  model_primary TEXT,
  project_path TEXT,
  git_identity TEXT
);
```

### 8.2 `daily_usage`

Purpose:

- persistent daily rollup table
- survives raw source deletion

Suggested schema:

```sql
CREATE TABLE daily_usage (
  date TEXT PRIMARY KEY,
  input_tokens INTEGER NOT NULL DEFAULT 0,
  output_tokens INTEGER NOT NULL DEFAULT 0,
  cache_creation_tokens INTEGER NOT NULL DEFAULT 0,
  cache_read_tokens INTEGER NOT NULL DEFAULT 0,
  total_tokens INTEGER NOT NULL DEFAULT 0,
  estimated_cost_usd REAL NOT NULL DEFAULT 0,
  session_count INTEGER NOT NULL DEFAULT 0,
  active_projects INTEGER NOT NULL DEFAULT 0,
  top_model TEXT,
  top_project TEXT,
  updated_at TEXT NOT NULL
);
```

### 8.3 `quota_snapshots`

Purpose:

- future capture of 5-hour and weekly quota states

Suggested schema:

```sql
CREATE TABLE quota_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  captured_at TEXT NOT NULL,
  window_type TEXT NOT NULL,
  usage_percent REAL NOT NULL,
  reset_at TEXT,
  source TEXT
);
```

### 8.4 `quota_events`

Purpose:

- future derived events such as limit hits and reset detection

Suggested schema:

```sql
CREATE TABLE quota_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  occurred_at TEXT NOT NULL,
  window_type TEXT NOT NULL,
  event_type TEXT NOT NULL,
  value_before REAL,
  value_after REAL,
  metadata_json TEXT
);
```

### 8.5 `achievements`

Purpose:

- store earned badge states

Suggested schema:

```sql
CREATE TABLE achievements (
  code TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  description TEXT,
  earned_at TEXT NOT NULL,
  value TEXT
);
```

### 8.6 `app_state`

Purpose:

- lightweight key-value state storage

Suggested schema:

```sql
CREATE TABLE app_state (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
```

## 9. Ingestion Strategy

### 9.1 Session Discovery

The collector should:

- scan configured Claude directories for candidate session JSONL files
- ignore unsupported files
- extract stable session UUIDs from filenames or contents

### 9.2 Deduplication

Deduplication key:

- `session_uuid`

Update behavior:

- if unseen session UUID: ingest
- if known session UUID but source mtime changed: recompute and update
- if raw file disappears later: do not delete `daily_usage`

### 9.3 Rollup Logic

MVP simplification:

- attribute a session to its session start date

Future enhancement:

- split multi-day sessions by message date

### 9.4 Raw Source Retention Independence

Important rule:

- persistent rollup tables must never be automatically deleted just because source JSONL files disappeared

This is a deliberate divergence from dashboard-style transient indexing systems.

## 10. Cost Estimation

The system should support estimated API-equivalent cost calculation.

Requirements:

- model-based pricing map
- configurable fallback behavior for unknown models
- support for:
  - input tokens
  - output tokens
  - cache creation tokens
  - cache read tokens

This calculation is approximate and should be labeled as estimated, not official billing.

## 11. Derived Product Metrics

The renderer and achievement engine will use derived metrics such as:

- daily total tokens
- monthly estimated value
- active day count
- current streak
- cache hit rate
- top model
- top project
- peak usage day
- monthly multiplier versus configured plan price

## 12. Rendering Design

### Output Assets

- `claude-grass.svg`
- `money-copy-card.svg`
- `claude-badges.svg`
- `profile-summary.json`

### 12.1 Claude Grass Renderer

Input:

- recent `daily_usage` rows

Output:

- contribution-style heatmap
- configurable intensity thresholds
- summary footer

Suggested summary fields:

- streak
- active days
- peak day
- recent total tokens

### 12.2 Money Copy Renderer

Input:

- current month aggregated usage
- configured monthly plan price

Output:

- estimated monthly value
- plan price multiplier
- monthly token total
- peak day
- top model

### 12.3 Badges Renderer

Input:

- derived achievement states

Output:

- badge strip or compact card

Suggested MVP badge rules:

- Night Shift Coder
- Weekend Grinder
- Cache Wizard
- Money Multiplier x5

## 13. Config Design

Suggested `config.toml`:

```toml
[paths]
claude_base = "C:/Users/82105/.claude"
profile_repo = "C:/Users/82105/Desktop/Subin9227"

[profile]
github_username = "Subin9227"
plan_monthly_price_usd = 20.0

[grass]
days = 180
levels = [0, 250000, 1000000, 3000000]

[output]
dir = "./output"
```

Config requirements:

- missing config should fail clearly
- paths should be validated
- defaults should be conservative where possible

## 14. Publisher Design

Publisher responsibilities:

- ensure output files exist
- copy them into configured profile repo asset directory
- optionally validate expected README asset paths

MVP should not auto-commit by default.

Reason:

- safer local workflow
- fewer accidental Git side effects

## 15. Error Handling Requirements

- Missing Claude directory should produce a clear warning or failure
- Invalid session files should be skipped with structured logging
- Unknown model pricing should fall back predictably
- Missing profile repo path should fail publish step only
- Render step should still work even if publish is skipped

## 16. Logging Requirements

Suggested logging output:

- sessions discovered
- sessions ingested
- sessions updated
- daily rollup rows updated
- assets generated
- files published

Logs should be readable in local CLI output first.

## 17. Testing Strategy

### Unit Tests

- session usage parsing
- cost calculation
- rollup aggregation
- streak calculation
- badge rule evaluation
- SVG text generation basics

### Integration Tests

- ingest fixture session files into SQLite
- generate expected output files
- re-run sync without duplication

### Manual Verification

- confirm output SVGs render in browser
- confirm copied assets display in GitHub README

## 18. Performance Considerations

MVP scale assumptions:

- single-user machine
- local SQLite
- modest number of local session files

Performance priorities:

- correctness first
- deduplication second
- rendering speed third

No special optimization work is required for MVP unless local scan time becomes noticeably slow.

## 19. Security and Privacy Considerations

- The product is local-first
- It should store rollups and lightweight session summaries, not full conversation archives
- Generated GitHub assets must avoid exposing private prompt contents
- Project names may reveal sensitive repo names, so configuration should eventually support redaction

## 20. Planned Post-MVP Extensions

- quota snapshot capture daemon or scheduler
- limit hit event detection
- weekly and monthly recap assets
- PNG export
- multi-machine state sync
- theme presets
- optional mini local dashboard

## 21. Implementation Phases

### Phase 1: Core Persistence

- initialize project
- SQLite schema
- session scanning
- session ingestion
- daily rollups

### Phase 2: Asset Generation

- grass SVG
- money card SVG
- badge SVG
- summary JSON

### Phase 3: Publishing Workflow

- profile repo sync
- README integration guidance

### Phase 4: Quota Tracking

- snapshot collection
- event derivation
- future badge expansion

