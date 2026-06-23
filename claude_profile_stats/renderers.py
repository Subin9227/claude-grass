from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path

from .metrics import calculate_streak, monthly_summary, pick_peak_day, total_recent_tokens


def _svg_text(x: int, y: int, text: str, size: int = 14, weight: int = 400, fill: str = "#e5e7eb") -> str:
    safe = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return (
        f'<text x="{x}" y="{y}" font-family="Segoe UI, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{safe}</text>'
    )


def _card(width: int, height: int, body: str, background: str = "#0f172a") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
        f'<rect width="{width}" height="{height}" rx="18" fill="{background}"/>'
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="17" fill="none" stroke="#1f2937"/>'
        f"{body}</svg>"
    )


def render_grass(rows: list[dict], output_path: Path, days: int, levels: list[int]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    end = date.today()
    start = end - timedelta(days=days - 1)
    by_date = {date.fromisoformat(row["date"]): row for row in rows}
    palette = ["#1f2937", "#134e4a", "#0f766e", "#14b8a6", "#5eead4"]

    cells = []
    current = start
    idx = 0
    cell_size = 12
    gap = 4
    cols = (days + 6) // 7
    while current <= end:
        row_idx = idx % 7
        col_idx = idx // 7
        x = 28 + col_idx * (cell_size + gap)
        y = 46 + row_idx * (cell_size + gap)
        total = by_date.get(current, {}).get("total_tokens", 0)
        if total <= levels[0]:
            level = 0
        elif total <= levels[1]:
            level = 1
        elif total <= levels[2]:
            level = 2
        elif total <= levels[3]:
            level = 3
        else:
            level = 4
        title = f"{current.isoformat()}: {total:,} tokens"
        cells.append(
            f'<g><title>{title}</title><rect x="{x}" y="{y}" width="{cell_size}" '
            f'height="{cell_size}" rx="3" fill="{palette[level]}"/></g>'
        )
        current += timedelta(days=1)
        idx += 1

    streak = calculate_streak(rows)
    active_days = sum(1 for row in rows if row["total_tokens"] > 0)
    peak_day = pick_peak_day(rows) or "n/a"
    recent_total = total_recent_tokens(rows, 30)
    width = max(360, 60 + cols * (cell_size + gap))
    body = "".join(
        [
            _svg_text(24, 28, "Claude Grass", 20, 700),
            _svg_text(width - 130, 28, f"Last {days} days", 12, 500, "#94a3b8"),
            *cells,
            _svg_text(24, 168, f"Streak {streak} days", 13, 600, "#cbd5e1"),
            _svg_text(150, 168, f"Active {active_days} days", 13, 600, "#cbd5e1"),
            _svg_text(298, 168, f"Peak {peak_day}", 13, 600, "#cbd5e1"),
            _svg_text(24, 192, f"Recent 30D {recent_total:,} tokens", 12, 500, "#94a3b8"),
        ]
    )
    output_path.write_text(_card(width, 212, body), encoding="utf-8")


def render_money_card(rows: list[dict], output_path: Path, plan_price: float) -> dict:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = monthly_summary(rows, plan_price)
    peak = summary["peak_day"] or "n/a"
    top_model = summary["top_model"] or "Unknown"
    body = "".join(
        [
            _svg_text(24, 32, "Money Copy", 20, 700),
            _svg_text(24, 76, f"${summary['estimated_cost_usd']:.2f}", 34, 800, "#f8fafc"),
            _svg_text(
                24,
                104,
                f"{summary['multiplier']}x of ${summary['plan_price_usd']:.0f} plan",
                14,
                500,
                "#94a3b8",
            ),
            _svg_text(24, 142, f"Month {summary['month_label']}", 13, 600),
            _svg_text(24, 170, f"Tokens {summary['total_tokens']:,}", 13, 500, "#cbd5e1"),
            _svg_text(200, 170, f"Peak Day {peak}", 13, 500, "#cbd5e1"),
            _svg_text(24, 194, f"Top Model {top_model}", 13, 500, "#cbd5e1"),
        ]
    )
    output_path.write_text(_card(440, 220, body, "#111827"), encoding="utf-8")
    return summary


def render_badges(achievements: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    visible = achievements[:4]
    if not visible:
        visible = [
            {
                "label": "Getting Started",
                "value": "Run sync",
            }
        ]
    pills = []
    x = 24
    y = 54
    for item in visible:
        label = item["label"]
        value = item.get("value") or ""
        width = max(120, 22 + len(label) * 8 + (len(value) * 6 if value else 0))
        pills.append(f'<rect x="{x}" y="{y}" width="{width}" height="44" rx="12" fill="#1e293b" stroke="#334155"/>')
        pills.append(_svg_text(x + 14, y + 19, label, 12, 700))
        if value:
            pills.append(_svg_text(x + 14, y + 35, value, 11, 500, "#93c5fd"))
        x += width + 12
    width = max(420, x)
    body = "".join([_svg_text(24, 30, "Claude Badges", 20, 700), *pills])
    output_path.write_text(_card(width, 124, body, "#0b1220"), encoding="utf-8")


def write_summary_json(
    rows: list[dict],
    monthly: dict,
    achievements: list[dict],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": date.today().isoformat(),
        "total_days": len(rows),
        "active_days": sum(1 for row in rows if row["total_tokens"] > 0),
        "streak_days": calculate_streak(rows),
        "peak_day": pick_peak_day(rows),
        "recent_30d_tokens": total_recent_tokens(rows, 30),
        "monthly": monthly,
        "achievements": achievements,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

