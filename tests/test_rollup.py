import sqlite3
import tempfile
import unittest
from pathlib import Path

from claude_profile_stats import db
from claude_profile_stats.collector import SessionSummary


def session(uuid, day, entrypoint="cli", model="claude-opus-4-8", tokens=100, cost=1.0):
    return SessionSummary(
        session_uuid=uuid,
        jsonl_path=Path(f"/x/{uuid}.jsonl"),
        source_mtime=1.0,
        session_start_at=f"{day}T00:00:00",
        session_end_at=f"{day}T01:00:00",
        session_date=day,
        input_tokens=tokens,
        output_tokens=0,
        cache_creation_tokens=0,
        cache_read_tokens=0,
        estimated_cost_usd=cost,
        model_primary=model,
        project_path="/x/proj",
        git_identity="x/proj",
        entrypoint=entrypoint,
        active_hours=[1],
        weekend=False,
    )


class RollupTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.conn = db.connect(Path(self._dir.name) / "t.db")

    def tearDown(self):
        self.conn.close()
        self._dir.cleanup()

    def test_rebuild_and_resync_does_not_double_count(self):
        sessions = [session("a", "2026-06-01"), session("b", "2026-06-01")]
        db.upsert_sessions(self.conn, sessions)
        db.rebuild_daily_usage(self.conn)
        rows = db.load_daily_usage(self.conn)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["session_count"], 2)
        self.assertEqual(rows[0]["total_tokens"], 200)

        # Re-running sync must not inflate the rollup.
        db.upsert_sessions(self.conn, sessions)
        db.rebuild_daily_usage(self.conn)
        rows = db.load_daily_usage(self.conn)
        self.assertEqual(rows[0]["session_count"], 2)
        self.assertEqual(rows[0]["total_tokens"], 200)

    def test_surface_breakdown_orders_by_tokens(self):
        db.upsert_sessions(
            self.conn,
            [
                session("a", "2026-06-01", entrypoint="cli", tokens=100),
                session("b", "2026-06-02", entrypoint="claude-vscode", tokens=300),
            ],
        )
        surfaces = db.load_surface_breakdown(self.conn)
        self.assertEqual(surfaces[0]["entrypoint"], "claude-vscode")
        self.assertEqual(surfaces[0]["total_tokens"], 300)
        self.assertEqual(surfaces[1]["entrypoint"], "cli")


class MigrationTests(unittest.TestCase):
    def test_connect_adds_entrypoint_column_to_old_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "old.db"
            legacy = sqlite3.connect(str(path))
            legacy.execute(
                "CREATE TABLE sessions_ingested ("
                "session_uuid TEXT PRIMARY KEY, jsonl_path TEXT NOT NULL, "
                "first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL, "
                "session_date TEXT NOT NULL)"
            )
            legacy.commit()
            legacy.close()

            conn = db.connect(path)
            columns = {r[1] for r in conn.execute("PRAGMA table_info(sessions_ingested)")}
            conn.close()
            self.assertIn("entrypoint", columns)


if __name__ == "__main__":
    unittest.main()
