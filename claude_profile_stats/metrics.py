from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta


def calculate_streak(rows: list[dict]) -> int:
    if not rows:
        return 0
    dates = {date.fromisoformat(row["date"]) for row in rows if row["total_tokens"] > 0}
    if not dates:
        return 0
    streak = 0
    cursor = max(dates)
    while cursor in dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def pick_peak_day(rows: list[dict]) -> str | None:
    if not rows:
        return None
    return max(rows, key=lambda item: item["total_tokens"])["date"]


def total_recent_tokens(rows: list[dict], days: int) -> int:
    if not rows:
        return 0
    cutoff = max(date.fromisoformat(rows[-1]["date"]) - timedelta(days=days - 1), date.min)
    return sum(row["total_tokens"] for row in rows if date.fromisoformat(row["date"]) >= cutoff)


def monthly_summary(rows: list[dict], plan_price: float) -> dict:
    today = date.today()
    monthly = [
        row
        for row in rows
        if (d := date.fromisoformat(row["date"])).year == today.year and d.month == today.month
    ]
    total_cost = sum(row["estimated_cost_usd"] for row in monthly)
    total_tokens = sum(row["total_tokens"] for row in monthly)
    top_models = Counter(row["top_model"] for row in monthly if row["top_model"])
    peak_day = pick_peak_day(monthly)
    return {
        "month_label": today.strftime("%B %Y"),
        "estimated_cost_usd": round(total_cost, 2),
        "plan_price_usd": plan_price,
        "multiplier": round(total_cost / plan_price, 2) if plan_price > 0 else 0.0,
        "total_tokens": total_tokens,
        "peak_day": peak_day,
        "top_model": top_models.most_common(1)[0][0] if top_models else None,
    }


def compute_achievements(rows: list[dict], monthly: dict) -> list[dict]:
    if not rows:
        return []

    earned_at = datetime.utcnow().isoformat()
    active_days = [row for row in rows if row["total_tokens"] > 0]
    weekend_days = sum(1 for row in rows if row["weekend_sessions"] > 0)
    all_hours = Counter(hour for row in rows for hour in row["active_hours"])
    night_hours = sum(count for hour, count in all_hours.items() if 0 <= hour <= 5)
    total_hours = sum(all_hours.values())
    cacheable = sum(
        row["input_tokens"] + row["cache_creation_tokens"] + row["cache_read_tokens"] for row in rows
    )
    cache_reads = sum(row["cache_read_tokens"] for row in rows)
    cache_rate = (cache_reads / cacheable) if cacheable > 0 else 0.0

    achievements = []
    if night_hours >= 10:
        achievements.append(
            {
                "code": "NIGHT_SHIFT_CODER",
                "label": "Night Shift Coder",
                "description": "Used Claude heavily during midnight hours.",
                "earned_at": earned_at,
                "value": str(night_hours),
            }
        )
    if weekend_days >= 8:
        achievements.append(
            {
                "code": "WEEKEND_GRINDER",
                "label": "Weekend Grinder",
                "description": "Stayed active across multiple weekends.",
                "earned_at": earned_at,
                "value": str(weekend_days),
            }
        )
    if cache_rate >= 0.5:
        achievements.append(
            {
                "code": "CACHE_WIZARD",
                "label": "Cache Wizard",
                "description": "Maintained a strong cache read rate.",
                "earned_at": earned_at,
                "value": f"{cache_rate:.0%}",
            }
        )
    if monthly["multiplier"] >= 5:
        achievements.append(
            {
                "code": "MONEY_MULTIPLIER",
                "label": "Money Multiplier",
                "description": "Generated at least 5x the configured plan value.",
                "earned_at": earned_at,
                "value": f"{monthly['multiplier']}x",
            }
        )
    if len(active_days) >= 30:
        achievements.append(
            {
                "code": "CONSISTENT_BUILDER",
                "label": "Consistent Builder",
                "description": "Built a strong habit with 30+ active days.",
                "earned_at": earned_at,
                "value": str(len(active_days)),
            }
        )
    return achievements

