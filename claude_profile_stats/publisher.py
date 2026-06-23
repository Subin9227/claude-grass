from __future__ import annotations

import shutil
from pathlib import Path

SECTION_START = "<!-- CLAUDE_PROFILE_STATS:START -->"
SECTION_END = "<!-- CLAUDE_PROFILE_STATS:END -->"


def build_profile_section(username: str) -> str:
    return f"""{SECTION_START}
## Claude Karma

![Money Copy](./assets/money-copy-card.svg)
![Claude Badges](./assets/claude-badges.svg)
![Claude Grass](./assets/claude-grass.svg)
<!-- generated for {username} -->
{SECTION_END}
"""


def _upsert_section(content: str, section: str) -> str:
    if SECTION_START in content and SECTION_END in content:
        start = content.index(SECTION_START)
        end = content.index(SECTION_END) + len(SECTION_END)
        replacement = section.strip()
        return f"{content[:start].rstrip()}\n\n{replacement}\n{content[end:].lstrip()}"
    trimmed = content.rstrip()
    if trimmed:
        return f"{trimmed}\n\n{section.strip()}\n"
    return f"{section.strip()}\n"


def publish_outputs(output_dir: Path, profile_repo: Path) -> list[Path]:
    assets_dir = profile_repo / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for filename in [
        "claude-grass.svg",
        "money-copy-card.svg",
        "claude-badges.svg",
        "profile-summary.json",
    ]:
        source = output_dir / filename
        if not source.exists():
            continue
        target = assets_dir / filename
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def write_profile_readme(profile_repo: Path, username: str) -> Path:
    profile_repo.mkdir(parents=True, exist_ok=True)
    readme_path = profile_repo / "README.md"
    existing = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    section = build_profile_section(username)
    readme_path.write_text(_upsert_section(existing, section), encoding="utf-8")
    return readme_path
