from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


MODEL_PRICING: dict[str, dict[str, float]] = {
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0, "input_long": 6.0, "output_long": 22.5},
    "claude-sonnet-4-20250514": {
        "input": 3.0,
        "output": 15.0,
        "input_long": 6.0,
        "output_long": 22.5,
    },
    "claude-opus-4-6": {"input": 5.0, "output": 25.0, "input_long": 10.0, "output_long": 37.5},
    "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
    "claude-3-7-sonnet-20250219": {"input": 3.0, "output": 15.0},
    "claude-3-5-haiku-20241022": {"input": 0.8, "output": 4.0},
}
DEFAULT_PRICING_MODEL = "claude-sonnet-4-6"
CACHE_WRITE_MULTIPLIER = 1.25
CACHE_READ_MULTIPLIER = 0.10
LONG_CONTEXT_THRESHOLD = 200_000


@dataclass
class SessionSummary:
    session_uuid: str
    jsonl_path: Path
    source_mtime: float
    session_start_at: str | None
    session_end_at: str | None
    session_date: str
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    estimated_cost_usd: float
    model_primary: str | None
    project_path: str | None
    git_identity: str | None
    active_hours: list[int]
    weekend: bool


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _resolve_pricing(model: str | None) -> dict[str, float]:
    if model in MODEL_PRICING:
        return MODEL_PRICING[model]
    model_lower = (model or "").lower()
    for known, pricing in MODEL_PRICING.items():
        family = known.split("-20")[0]
        if family in model_lower:
            return pricing
    return MODEL_PRICING[DEFAULT_PRICING_MODEL]


def _calculate_cost(
    model: str | None,
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int,
    cache_read_tokens: int,
) -> float:
    pricing = _resolve_pricing(model)
    total_context = input_tokens + cache_creation_tokens + cache_read_tokens
    is_long = total_context > LONG_CONTEXT_THRESHOLD and "input_long" in pricing
    input_price = pricing.get("input_long", pricing["input"]) if is_long else pricing["input"]
    output_price = pricing.get("output_long", pricing["output"]) if is_long else pricing["output"]
    return round(
        (input_tokens / 1_000_000) * input_price
        + (cache_creation_tokens / 1_000_000) * input_price * CACHE_WRITE_MULTIPLIER
        + (cache_read_tokens / 1_000_000) * input_price * CACHE_READ_MULTIPLIER
        + (output_tokens / 1_000_000) * output_price,
        6,
    )


def _normalize_git_identity(project_path: str | None) -> str | None:
    if not project_path:
        return None
    lowered = project_path.replace("\\", "/").rstrip("/").lower()
    parts = [part for part in lowered.split("/") if part]
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return parts[-1] if parts else None


def _extract_message_payload(entry: dict) -> dict:
    nested = entry.get("message")
    return nested if isinstance(nested, dict) else entry


def collect_sessions(claude_base: Path) -> list[SessionSummary]:
    projects_dir = claude_base / "projects"
    if not projects_dir.exists():
        return []

    sessions: list[SessionSummary] = []
    for project_dir in sorted(projects_dir.iterdir()):
        if not project_dir.is_dir():
            continue
        for jsonl_path in sorted(project_dir.glob("*.jsonl")):
            if jsonl_path.name.startswith("agent-"):
                continue
            summary = parse_session_file(jsonl_path)
            if summary is not None:
                sessions.append(summary)
    return sessions


def parse_session_file(jsonl_path: Path) -> SessionSummary | None:
    input_tokens = 0
    output_tokens = 0
    cache_creation_tokens = 0
    cache_read_tokens = 0
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    model_primary: str | None = None
    project_path: str | None = None
    active_hours: set[int] = set()

    try:
        with jsonl_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                payload = _extract_message_payload(entry)
                timestamp = _parse_timestamp(entry.get("timestamp") or payload.get("timestamp"))
                if timestamp is not None:
                    if first_ts is None:
                        first_ts = timestamp
                    last_ts = timestamp
                    local_dt = timestamp.astimezone()
                    active_hours.add(local_dt.hour)

                if project_path is None:
                    cwd = entry.get("cwd") or payload.get("cwd")
                    if isinstance(cwd, str) and cwd:
                        project_path = cwd

                if entry.get("type") != "assistant":
                    continue

                if model_primary is None:
                    model_primary = payload.get("model")

                usage = payload.get("usage")
                if not isinstance(usage, dict):
                    continue
                input_tokens += int(usage.get("input_tokens", 0) or 0)
                output_tokens += int(usage.get("output_tokens", 0) or 0)
                cache_creation_tokens += int(usage.get("cache_creation_input_tokens", 0) or 0)
                cache_read_tokens += int(usage.get("cache_read_input_tokens", 0) or 0)
    except OSError:
        return None

    if first_ts is None:
        first_ts = datetime.fromtimestamp(jsonl_path.stat().st_mtime, tz=timezone.utc)
    if last_ts is None:
        last_ts = first_ts

    session_date = first_ts.astimezone().date().isoformat()
    estimated_cost_usd = _calculate_cost(
        model_primary,
        input_tokens,
        output_tokens,
        cache_creation_tokens,
        cache_read_tokens,
    )
    weekday = first_ts.astimezone().weekday()
    return SessionSummary(
        session_uuid=jsonl_path.stem,
        jsonl_path=jsonl_path,
        source_mtime=jsonl_path.stat().st_mtime,
        session_start_at=first_ts.isoformat(),
        session_end_at=last_ts.isoformat(),
        session_date=session_date,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_creation_tokens=cache_creation_tokens,
        cache_read_tokens=cache_read_tokens,
        estimated_cost_usd=estimated_cost_usd,
        model_primary=model_primary,
        project_path=project_path,
        git_identity=_normalize_git_identity(project_path),
        active_hours=sorted(active_hours),
        weekend=weekday >= 5,
    )

