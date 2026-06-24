import unittest
from datetime import date, timedelta

from claude_profile_stats.metrics import (
    calculate_longest_streak,
    calculate_streak,
    compute_achievements,
    monthly_summary,
)


def row(day, tokens=1000, **extra):
    base = {
        "date": day,
        "total_tokens": tokens,
        "estimated_cost_usd": 0.0,
        "top_model": "claude-opus-4-8",
        "weekend_sessions": 0,
        "input_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0,
        "active_hours": [],
    }
    base.update(extra)
    return base


class StreakTests(unittest.TestCase):
    def test_current_streak_counts_from_today(self):
        today = date.today()
        rows = [row((today - timedelta(days=i)).isoformat()) for i in range(3)]
        self.assertEqual(calculate_streak(rows), 3)

    def test_streak_is_zero_when_last_activity_is_stale(self):
        old = date.today() - timedelta(days=10)
        rows = [row((old - timedelta(days=i)).isoformat()) for i in range(3)]
        self.assertEqual(calculate_streak(rows), 0)

    def test_streak_counts_from_yesterday(self):
        yesterday = date.today() - timedelta(days=1)
        rows = [row((yesterday - timedelta(days=i)).isoformat()) for i in range(2)]
        self.assertEqual(calculate_streak(rows), 2)

    def test_longest_streak_picks_longest_run(self):
        rows = [
            row("2026-01-01"),
            row("2026-01-02"),
            row("2026-01-03"),  # run of 3
            row("2026-01-10"),  # gap
            row("2026-01-11"),  # run of 2
        ]
        self.assertEqual(calculate_longest_streak(rows), 3)

    def test_inactive_days_excluded(self):
        rows = [row("2026-01-01", tokens=0), row("2026-01-02", tokens=5)]
        self.assertEqual(calculate_longest_streak(rows), 1)
        self.assertEqual(calculate_streak([]), 0)


class MonthlyTests(unittest.TestCase):
    def test_multiplier_and_totals(self):
        first_of_month = date.today().replace(day=1).isoformat()
        rows = [row(first_of_month, tokens=100, estimated_cost_usd=40.0)]
        summary = monthly_summary(rows, 20.0)
        self.assertEqual(summary["estimated_cost_usd"], 40.0)
        self.assertEqual(summary["multiplier"], 2.0)
        self.assertEqual(summary["total_tokens"], 100)


class BadgeTests(unittest.TestCase):
    def test_cache_wizard_and_money_multiplier(self):
        rows = [row("2026-06-01", input_tokens=100, cache_read_tokens=900)]
        codes = {a["code"] for a in compute_achievements(rows, {"multiplier": 6.0})}
        self.assertIn("CACHE_WIZARD", codes)  # 900 / 1000 = 0.9 >= 0.5
        self.assertIn("MONEY_MULTIPLIER", codes)

    def test_no_badges_for_empty_history(self):
        self.assertEqual(compute_achievements([], {"multiplier": 0.0}), [])


if __name__ == "__main__":
    unittest.main()
