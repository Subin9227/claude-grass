from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .collector import collect_sessions
from .config import AppConfig, load_config
from .db import connect, load_achievements, load_daily_usage, rebuild_daily_usage, replace_achievements, upsert_sessions
from .metrics import compute_achievements, monthly_summary
from .publisher import publish_outputs, write_profile_readme
from .renderers import render_badges, render_grass, render_money_card, write_summary_json


def run_sync(config: AppConfig) -> None:
    sessions = collect_sessions(config.paths.claude_base)
    conn = connect(config.paths.database)
    upsert_sessions(conn, sessions)
    rebuild_daily_usage(conn)
    rows = load_daily_usage(conn)
    monthly = monthly_summary(rows, config.profile.plan_monthly_price_usd)
    achievements = compute_achievements(rows, monthly)
    replace_achievements(conn, achievements)
    print(f"Synced {len(sessions)} sessions into {config.paths.database}")


def run_render(config: AppConfig) -> None:
    conn = connect(config.paths.database)
    rows = load_daily_usage(conn)
    achievements = load_achievements(conn)
    monthly = render_money_card(
        rows,
        config.paths.output_dir / "money-copy-card.svg",
        config.profile.plan_monthly_price_usd,
    )
    render_grass(
        rows,
        config.paths.output_dir / "claude-grass.svg",
        config.grass.days,
        config.grass.levels,
    )
    render_badges(achievements, config.paths.output_dir / "claude-badges.svg")
    write_summary_json(rows, monthly, achievements, config.paths.output_dir / "profile-summary.json")
    print(f"Rendered assets into {config.paths.output_dir}")


def run_publish(config: AppConfig) -> None:
    copied = publish_outputs(config.paths.output_dir, config.paths.profile_repo)
    readme_path = write_profile_readme(config.paths.profile_repo, config.profile.github_username)
    print(
        f"Published {len(copied)} files into {config.paths.profile_repo / 'assets'} "
        f"and wrote {readme_path}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Claude Profile Stats")
    parser.add_argument(
        "command",
        choices=["sync", "render", "publish", "all"],
        help="Command to run",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.toml",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_config(args.config)

    if args.command == "sync":
        run_sync(config)
    elif args.command == "render":
        run_render(config)
    elif args.command == "publish":
        run_publish(config)
    elif args.command == "all":
        run_sync(config)
        run_render(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
