# Claude Profile Stats

Local-first Claude usage tracker that:

- ingests local Claude session JSONL files
- persists daily usage rollups in SQLite
- renders GitHub-profile-ready SVG assets

## Commands

```bash
python -m claude_profile_stats.app sync
python -m claude_profile_stats.app render
python -m claude_profile_stats.app all
python -m claude_profile_stats.app publish
```

## Outputs

- `output/claude-grass.svg`
- `output/money-copy-card.svg`
- `output/claude-badges.svg`
- `output/profile-summary.json`

## Config

Copy `config.toml.example` to `config.toml` and adjust paths as needed.

