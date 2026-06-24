from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import date, datetime
import json
from pathlib import Path
import sqlite3

from .collector import SessionSummary


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions_ingested (
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
  git_identity TEXT,
  entrypoint TEXT,
  active_hours_json TEXT NOT NULL DEFAULT '[]',
  weekend INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS daily_usage (
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
  weekend_sessions INTEGER NOT NULL DEFAULT 0,
  active_hours_json TEXT NOT NULL DEFAULT '[]',
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS achievements (
  code TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  description TEXT,
  earned_at TEXT NOT NULL,
  value TEXT
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    _ensure_columns(conn)
    return conn


def _ensure_columns(conn: sqlite3.Connection) -> None:
    """Add columns introduced after a DB was first created (lightweight migration)."""
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(sessions_ingested)")}
    if "entrypoint" not in existing:
        conn.execute("ALTER TABLE sessions_ingested ADD COLUMN entrypoint TEXT")
        conn.commit()


def upsert_sessions(conn: sqlite3.Connection, sessions: list[SessionSummary]) -> None:
    now = datetime.utcnow().isoformat()
    for session in sessions:
        existing = conn.execute(
            "SELECT source_mtime, first_seen_at FROM sessions_ingested WHERE session_uuid = ?",
            (session.session_uuid,),
        ).fetchone()
        first_seen_at = existing["first_seen_at"] if existing else now
        conn.execute(
            """
            INSERT OR REPLACE INTO sessions_ingested (
              session_uuid, jsonl_path, source_mtime, first_seen_at, last_seen_at,
              session_start_at, session_end_at, session_date, input_tokens, output_tokens,
              cache_creation_tokens, cache_read_tokens, estimated_cost_usd, model_primary,
              project_path, git_identity, entrypoint, active_hours_json, weekend
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session.session_uuid,
                str(session.jsonl_path),
                session.source_mtime,
                first_seen_at,
                now,
                session.session_start_at,
                session.session_end_at,
                session.session_date,
                session.input_tokens,
                session.output_tokens,
                session.cache_creation_tokens,
                session.cache_read_tokens,
                session.estimated_cost_usd,
                session.model_primary,
                session.project_path,
                session.git_identity,
                session.entrypoint,
                json.dumps(session.active_hours),
                1 if session.weekend else 0,
            ),
        )
    conn.commit()


def rebuild_daily_usage(conn: sqlite3.Connection) -> None:
    rows = conn.execute("SELECT * FROM sessions_ingested").fetchall()
    aggregate: dict[str, dict] = {}
    for row in rows:
        bucket = aggregate.setdefault(
            row["session_date"],
            {
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_creation_tokens": 0,
                "cache_read_tokens": 0,
                "estimated_cost_usd": 0.0,
                "session_count": 0,
                "projects": set(),
                "models": Counter(),
                "hours": set(),
                "weekend_sessions": 0,
                "top_project": Counter(),
            },
        )
        bucket["input_tokens"] += row["input_tokens"]
        bucket["output_tokens"] += row["output_tokens"]
        bucket["cache_creation_tokens"] += row["cache_creation_tokens"]
        bucket["cache_read_tokens"] += row["cache_read_tokens"]
        bucket["estimated_cost_usd"] += row["estimated_cost_usd"]
        bucket["session_count"] += 1
        if row["git_identity"]:
            bucket["projects"].add(row["git_identity"])
            bucket["top_project"][row["git_identity"]] += 1
        elif row["project_path"]:
            bucket["projects"].add(row["project_path"])
            bucket["top_project"][row["project_path"]] += 1
        if row["model_primary"]:
            bucket["models"][row["model_primary"]] += 1
        for hour in json.loads(row["active_hours_json"] or "[]"):
            bucket["hours"].add(int(hour))
        bucket["weekend_sessions"] += int(row["weekend"])

    conn.execute("DELETE FROM daily_usage")
    now = datetime.utcnow().isoformat()
    for day, data in aggregate.items():
        conn.execute(
            """
            INSERT INTO daily_usage (
              date, input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens,
              total_tokens, estimated_cost_usd, session_count, active_projects,
              top_model, top_project, weekend_sessions, active_hours_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                day,
                data["input_tokens"],
                data["output_tokens"],
                data["cache_creation_tokens"],
                data["cache_read_tokens"],
                data["input_tokens"]
                + data["output_tokens"]
                + data["cache_creation_tokens"]
                + data["cache_read_tokens"],
                round(data["estimated_cost_usd"], 6),
                data["session_count"],
                len(data["projects"]),
                data["models"].most_common(1)[0][0] if data["models"] else None,
                data["top_project"].most_common(1)[0][0] if data["top_project"] else None,
                data["weekend_sessions"],
                json.dumps(sorted(data["hours"])),
                now,
            ),
        )
    conn.commit()


def load_daily_usage(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM daily_usage ORDER BY date").fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["active_hours"] = json.loads(item.pop("active_hours_json", "[]"))
        result.append(item)
    return result


def replace_achievements(conn: sqlite3.Connection, achievements: list[dict]) -> None:
    conn.execute("DELETE FROM achievements")
    for item in achievements:
        conn.execute(
            "INSERT INTO achievements (code, label, description, earned_at, value) VALUES (?, ?, ?, ?, ?)",
            (
                item["code"],
                item["label"],
                item["description"],
                item["earned_at"],
                item["value"],
            ),
        )
    conn.commit()


def load_achievements(conn: sqlite3.Connection) -> list[dict]:
    return [dict(row) for row in conn.execute("SELECT * FROM achievements ORDER BY earned_at, code")]


def load_surface_breakdown(conn: sqlite3.Connection) -> list[dict]:
    """Token totals grouped by client surface (cli / vscode / desktop / ...)."""
    rows = conn.execute(
        """
        SELECT
          COALESCE(NULLIF(entrypoint, ''), 'unknown') AS entrypoint,
          SUM(input_tokens + output_tokens + cache_creation_tokens + cache_read_tokens)
            AS total_tokens,
          SUM(estimated_cost_usd) AS estimated_cost_usd,
          COUNT(*) AS session_count
        FROM sessions_ingested
        GROUP BY COALESCE(NULLIF(entrypoint, ''), 'unknown')
        ORDER BY total_tokens DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]

