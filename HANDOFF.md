# Handoff

## Project

Claude Grass

Repository:

- GitHub repo for this project: `Subin9227/claude-grass`
- GitHub profile repo used for generated assets: `Subin9227/Subin9227`

## Goal

Build a local-first Claude usage tracker that:

- reads Claude local session logs
- persists usage history beyond raw session retention
- generates GitHub-profile-ready SVG assets

Current visible outputs:

1. Claude Grass
2. Money Copy Card
3. Claude Badges

## What Was Decided

- Do not build this on top of the previously reviewed `claude-code-karma` repo.
- Use that repo only as reference for Claude local storage structure and usage parsing ideas.
- Build a lighter new project focused on:
  - local ingestion
  - persistent rollups
  - SVG asset generation
  - GitHub profile publishing

## Current Implementation Status

Implemented:

- local Python project structure
- config loading
- Claude local session scan from `~/.claude/projects`
- session usage parsing
- SQLite persistence
- daily rollup rebuild
- SVG rendering for:
  - `claude-grass.svg`
  - `money-copy-card.svg`
  - `claude-badges.svg`
- summary JSON generation
- publish step that copies outputs into a profile repo
- publish step updates README by inserting/updating only a managed section

Not implemented yet:

- quota snapshot tracking
- 5-hour limit hit detection
- weekly limit event tracking
- multi-machine merge/sync
- polished SVG design
- automated GitHub Actions publishing

## Important Files

Core code:

- `claude_profile_stats/app.py`
- `claude_profile_stats/collector.py`
- `claude_profile_stats/config.py`
- `claude_profile_stats/db.py`
- `claude_profile_stats/metrics.py`
- `claude_profile_stats/renderers.py`
- `claude_profile_stats/publisher.py`

Docs:

- `PRD.md`
- `TRD.md`
- `USER_GUIDE.md`

Config:

- `config.toml.example`
- local machine-specific `config.toml` is ignored by git

## Managed README Behavior

Important:

- Earlier publish logic overwrote the whole profile `README.md`.
- This was fixed.
- Current behavior uses markers:
  - `<!-- CLAUDE_PROFILE_STATS:START -->`
  - `<!-- CLAUDE_PROFILE_STATS:END -->`
- Only that section should be replaced on future publish runs.

## Local Run Commands

Generate usage rollups and SVG outputs:

```bash
python -m claude_profile_stats.app all --config config.toml
```

Copy generated outputs into profile repo:

```bash
python -m claude_profile_stats.app publish --config config.toml
```

## Typical Folder Layout

Example layout used during development:

```text
C:\Users\82105\Desktop\
  claude-dashboard\
  Subin9227-profile\
```

Notes:

- `claude-dashboard` is the local project working folder
- `Subin9227-profile` is a clone of the GitHub profile repo

## Git Ignore Notes

These should not be pushed from the main project repo:

- `repo/` (reference repo clone)
- `profile-preview/` (local demo profile folder)
- `data/`
- `output/`
- `config.toml`

## Known Gotchas

### 1. Python 3.10 TOML support

- Python 3.10 does not have built-in `tomllib`
- a simple fallback parser was added in `config.py`

### 2. Publish does not push to GitHub automatically

- `publish` only copies files to the local profile repo path
- user still needs:
  - `git add`
  - `git commit`
  - `git push`

### 3. Broken images on GitHub

If images show as broken on GitHub:

- the README likely references `./assets/*.svg`
- but those asset files were not committed/pushed in the profile repo

### 4. Multi-machine data is not merged

- the current tool reads local Claude records from the current machine only
- using multiple computers will not automatically combine histories

## Suggested Next Steps

1. Improve SVG visual quality
2. Add quota snapshot tracking
3. Add limit-hit badges/events
4. Improve open-source README and onboarding
5. Add optional scheduled local sync

## If Resuming On Another Computer

Recommended sequence:

1. Clone `Subin9227/claude-grass`
2. Clone your GitHub profile repo
3. Create `config.toml`
4. Run:

```bash
python -m claude_profile_stats.app all --config config.toml
python -m claude_profile_stats.app publish --config config.toml
```

5. Commit/push from the profile repo

