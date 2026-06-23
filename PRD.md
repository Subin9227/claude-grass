# Claude Profile Stats PRD

## Document Status

- Status: Draft v0
- Date: 2026-06-24
- Owner: Subin
- Notes: This document is an initial product requirements draft based on planning discussions. It is expected to change after implementation and early usage.

## 1. Product Summary

Claude Profile Stats is a local-first personal analytics tool that tracks Claude usage from the user's machine, preserves meaningful history beyond Claude's rolling local retention window, and generates GitHub Profile README assets that make usage feel shareable and fun.

The product is designed around three visible outputs:

1. Claude Grass
2. Money Copy Card
3. Claude Badges

These outputs are generated as static SVG assets and embedded in the user's GitHub Profile README.

## 2. Problem Statement

Developers who use Claude heavily want more than a temporary session view:

- They want to know how much they used Claude today, this week, and this month.
- They want their usage history to survive beyond Claude's local session cleanup window.
- They want a playful, public-facing way to show effort and intensity, similar to GitHub contribution graphs.
- They want "flex" artifacts such as badges, usage streaks, and "money copied" summaries.

Existing local dashboards focus mostly on recent session inspection. They do not primarily solve long-lived personal history and GitHub-profile-ready outputs.

## 3. Product Vision

Turn Claude usage into a personal developer identity layer:

- useful enough to track real usage
- durable enough to outlive raw session logs
- fun enough to share on GitHub

## 4. Target User

Primary user:

- Individual Claude power user
- Uses Claude Code or Claude local session storage regularly
- Wants personal analytics and GitHub profile visuals

Secondary future user:

- Other developers who want a plug-and-play personal usage visualizer

## 5. Goals

### Primary Goals

- Persist daily Claude usage history locally, even after raw session logs disappear
- Generate GitHub Profile README-ready SVG assets
- Provide a simple local sync workflow
- Make usage feel motivating and playful

### Secondary Goals

- Track quota-related events from the moment the tool starts running
- Support future expansion into richer dashboards or exports

## 6. Non-Goals for MVP

- Team analytics
- Multi-user auth
- Hosted SaaS product
- Full browser dashboard
- Perfect historical reconstruction before installation
- Full conversation archival
- Official Anthropic account/API-based billing truth

## 7. Core Use Cases

### Use Case 1: Track My Claude Usage

As a user, I want the tool to scan my local Claude data and preserve daily usage totals so I can see long-term patterns.

### Use Case 2: Keep My History After Raw Logs Expire

As a user, I want daily rollups to remain even after Claude deletes older local session logs.

### Use Case 3: Show My Usage on GitHub

As a user, I want generated SVG assets that I can place in my GitHub Profile README.

### Use Case 4: Flex My Heavy Usage

As a user, I want badges and summary cards that make my Claude usage feel like achievements.

### Use Case 5: Track Limit Hits Going Forward

As a user, I want future 5-hour and weekly usage window events recorded from the moment I enable tracking.

## 8. MVP Scope

### Included in MVP

- Local Claude session scanning
- SQLite-based persistent rollups
- Deduplicated session ingestion
- Daily usage persistence
- SVG generation for:
  - Claude Grass
  - Money Copy Card
  - Claude Badges
- JSON summary export
- Publish-to-profile-repo workflow

### Deferred but Planned

- Quota snapshot capture
- Limit hit detection
- Reset event tracking
- Automatic scheduler setup
- More advanced badge systems
- Shareable PNG rendering

## 9. User Experience Overview

The intended user flow:

1. User installs the tool locally
2. User configures Claude path and GitHub profile repo path
3. User runs a sync command
4. Tool scans Claude local session data
5. Tool updates persistent rollups
6. Tool generates README-ready SVG assets
7. User commits generated assets to GitHub profile repo

Longer-term expected rhythm:

- Run manually
- Or run on a local schedule
- Periodically push updated profile visuals

## 10. Feature Requirements

### 10.1 Claude Grass

Purpose:

- Provide a GitHub contribution graph style view of Claude usage intensity over time

Requirements:

- Show recent daily activity over a configurable lookback period
- Use color intensity buckets
- Survive raw session deletion because data comes from persistent rollups
- Display summary stats such as active days, streak, and peak day

Success criteria:

- A user can glance at the asset and understand their recent Claude intensity pattern

### 10.2 Money Copy Card

Purpose:

- Show how much Claude value the user extracted relative to a configured monthly plan price

Requirements:

- Show current month estimated API-equivalent value
- Show multiplier versus configured plan price
- Show monthly token total
- Show peak usage day
- Show top model if available

Success criteria:

- A user feels the output is both informative and fun to share

### 10.3 Claude Badges

Purpose:

- Turn usage patterns into identity-like achievements

Requirements:

- Generate badges from local aggregate metrics
- Support at least a small set of MVP badges
- Badge logic must be deterministic and locally reproducible

Candidate MVP badges:

- Night Shift Coder
- Weekend Grinder
- Cache Wizard
- Money Multiplier

Success criteria:

- At least one user can immediately understand why they earned a badge

### 10.4 Persistent Rollups

Purpose:

- Preserve useful history beyond Claude's raw log retention

Requirements:

- Persist daily usage independently of raw JSONL lifetime
- Avoid duplicate session ingestion
- Support re-sync without double counting

Success criteria:

- Older days remain visible in generated assets even if source logs are gone

### 10.5 Profile Publish Workflow

Purpose:

- Make GitHub profile updating easy

Requirements:

- Output SVG files to a predictable directory
- Support copying files into a separate GitHub profile repo
- Keep README integration simple

Success criteria:

- User can update their profile assets in one repeatable local workflow

## 11. Functional Requirements

- The system must read Claude local session files from a configurable base path
- The system must parse assistant usage metadata from local session logs
- The system must aggregate usage into persistent daily rollups
- The system must deduplicate sessions by stable identifier
- The system must preserve aggregate data even when source sessions disappear
- The system must generate static SVG assets
- The system must generate a machine-readable summary JSON file
- The system should support configurable plan price and lookback windows
- The system should support future quota snapshot tracking

## 12. Success Metrics

### MVP Success Metrics

- User can generate all three SVG assets successfully on their machine
- At least 30+ days of usage remains visible after some raw logs disappear
- User can embed assets in GitHub Profile README with no runtime backend
- Daily sync can be rerun without corrupting aggregate history

### Qualitative Success Metrics

- The assets feel "share-worthy"
- The visuals feel distinct from generic GitHub widgets
- The tool makes Claude usage feel legible and motivating

## 13. Risks

- Claude local storage format may change
- Raw quota information may not be directly available locally
- Cost estimates may differ from official billing behavior
- A purely local workflow may feel manual unless scheduling is added
- GitHub profile asset design may need iteration to avoid looking generic

## 14. Open Questions

- What is the exact best source for quota snapshots in the local environment?
- Should daily usage be attributed by session start date or split across message dates?
- Should profile publishing eventually commit automatically or remain manual?
- Should the project eventually support optional PNG export for social sharing?

## 15. Future Opportunities

- Limit hit trophies
- Weekly and monthly recap cards
- Shareable image packs
- Local mini dashboard
- Multi-machine sync
- Theme variants for profile assets

