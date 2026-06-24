# Claude Profile Stats

Local-first Claude usage tracker that:

- ingests local Claude session JSONL files
- persists daily usage rollups in SQLite
- renders GitHub-profile-ready SVG assets

## Measurement scope

This tool reads **Claude Code usage on the current machine** — sessions logged
under `~/.claude/projects` (terminal CLI, the VS Code/JetBrains extension, and
desktop-initiated agent sessions). The `surfaces` field in
`profile-summary.json` breaks usage down by client (`cli` / `claude-vscode` /
`claude-desktop`).

It does **not** include claude.ai web chat (no local token logs exist for it)
or usage from other machines. Updates are manual — re-run the commands below
and push; there is no automatic/scheduled sync yet.

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

