"""Generate the sample cards shown in the README, from synthetic data.

These are committed under ``docs/images/`` so the README has a stable demo that
exposes no real usage. Run with::

    python scripts/generate_sample_assets.py
"""

from __future__ import annotations

import random
import sys
from datetime import date, timedelta
from pathlib import Path

# Allow running directly (python scripts/generate_sample_assets.py) without install.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from claude_profile_stats.renderers import (  # noqa: E402
    render_badges,
    render_grass,
    render_money_card,
)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"
GRASS_DAYS = 120

SAMPLE_BADGES = [
    {"label": "Night Shift Coder", "value": "42"},
    {"label": "Cache Wizard", "value": "88%"},
    {"label": "Money Multiplier", "value": "7.5x"},
    {"label": "Consistent Builder", "value": "60"},
]


def build_rows(days: int = GRASS_DAYS) -> list[dict]:
    random.seed(7)  # deterministic so the samples don't churn on every run
    today = date.today()
    rows: list[dict] = []
    for offset in range(days):
        day = today - timedelta(days=days - 1 - offset)
        days_ago = days - 1 - offset
        active = days_ago < 6 or random.random() > 0.25  # keep a fresh streak
        tokens = random.randint(200_000, 4_000_000) if active else 0
        rows.append(
            {
                "date": day.isoformat(),
                "total_tokens": tokens,
                "input_tokens": int(tokens * 0.10),
                "output_tokens": int(tokens * 0.10),
                "cache_creation_tokens": int(tokens * 0.20),
                "cache_read_tokens": int(tokens * 0.60),
                "estimated_cost_usd": round(tokens / 1_000_000 * 6.0, 2),
                "top_model": "claude-opus-4-8",
                "weekend_sessions": 1 if day.weekday() >= 5 and active else 0,
                "active_hours": [9, 10, 22, 23] if active else [],
            }
        )
    return rows


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    render_money_card(rows, OUTPUT_DIR / "money-copy-card.svg", 20.0)
    render_grass(rows, OUTPUT_DIR / "claude-grass.svg", GRASS_DAYS, [0, 250000, 1000000, 3000000])
    render_badges(SAMPLE_BADGES, OUTPUT_DIR / "claude-badges.svg")
    print(f"Wrote sample cards into {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
