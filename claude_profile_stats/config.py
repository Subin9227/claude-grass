from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:  # pragma: no cover - no TOML parser installed
        tomllib = None  # type: ignore[assignment]


def _parse_scalar(value: str):
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",")]
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _load_simple_toml(path: Path) -> dict:
    data: dict[str, dict] = {}
    current: dict | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section_name = line[1:-1].strip()
            current = data.setdefault(section_name, {})
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        target = current if current is not None else data
        target[key.strip()] = _parse_scalar(value)
    return data


@dataclass(frozen=True)
class PathsConfig:
    claude_base: Path
    profile_repo: Path
    database: Path
    output_dir: Path


@dataclass(frozen=True)
class ProfileConfig:
    github_username: str
    plan_monthly_price_usd: float


@dataclass(frozen=True)
class GrassConfig:
    days: int
    levels: list[int]


@dataclass(frozen=True)
class AppConfig:
    paths: PathsConfig
    profile: ProfileConfig
    grass: GrassConfig


def _default_config() -> AppConfig:
    home = Path.home()
    root = Path.cwd()
    return AppConfig(
        paths=PathsConfig(
            claude_base=home / ".claude",
            profile_repo=home / "Desktop" / "github-profile",
            database=root / "data" / "profile.db",
            output_dir=root / "output",
        ),
        profile=ProfileConfig(
            github_username="github-user",
            plan_monthly_price_usd=20.0,
        ),
        grass=GrassConfig(days=180, levels=[0, 250000, 1000000, 3000000]),
    )


def load_config(config_path: Path | None = None) -> AppConfig:
    defaults = _default_config()
    path = config_path or (Path.cwd() / "config.toml")
    if not path.exists():
        return defaults

    if tomllib is None:
        raw = _load_simple_toml(path)
    else:
        with path.open("rb") as handle:
            raw = tomllib.load(handle)

    paths = raw.get("paths", {})
    profile = raw.get("profile", {})
    grass = raw.get("grass", {})

    return AppConfig(
        paths=PathsConfig(
            claude_base=Path(paths.get("claude_base", defaults.paths.claude_base)),
            profile_repo=Path(paths.get("profile_repo", defaults.paths.profile_repo)),
            database=Path(paths.get("database", defaults.paths.database)),
            output_dir=Path(paths.get("output_dir", defaults.paths.output_dir)),
        ),
        profile=ProfileConfig(
            github_username=profile.get("github_username", defaults.profile.github_username),
            plan_monthly_price_usd=float(
                profile.get("plan_monthly_price_usd", defaults.profile.plan_monthly_price_usd)
            ),
        ),
        grass=GrassConfig(
            days=int(grass.get("days", defaults.grass.days)),
            levels=[int(level) for level in grass.get("levels", defaults.grass.levels)],
        ),
    )
