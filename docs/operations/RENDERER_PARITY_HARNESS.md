# Renderer Parity Harness

The renderer parity harness checks whether projection outputs preserve the meaning of canonical view models. It is intentionally conservative: it validates labels, JSON paths, and unsafe claims rather than trying to judge visual fidelity.

## Why It Exists

Track A now has canonical view-model contracts, design-token contracts, and a SearchPage dry-run projection. Before production renderers or static refactors, Eureka needs a repeatable way to prove that a projection did not drop source, evidence, status, rights, risk, limitation, gap, action, or capability-boundary meaning.

## Current Scope

The active case is `search_page_static_projection_v0`. It checks the TRACK-A-13 dry-run outputs:

- standard static HTML
- lite static HTML
- plain text
- file-tree README text
- static JSON handoff

ObjectPage, SourcePage, NeedPage, and CandidatePage cases are represented as future placeholders and skipped by the runner until later dry-run outputs exist.

## Commands

```powershell
python scripts/validate_renderer_parity_harness.py
python scripts/run_renderer_parity_harness.py --list
python scripts/run_renderer_parity_harness.py --check
python scripts/run_renderer_parity_harness.py --case search_page_static_projection_v0 --check
python scripts/run_renderer_parity_harness.py --json-output control/audits/track-a-16-renderer-parity-harness-v0/renderer_parity_report.json
```

The runner writes no files by default. It never regenerates `site/dist` and never calls networks, models, providers, or external APIs.

## Semantic Checks

The current SearchPage case checks route identity, view identity, query identity, result identity, source and evidence posture, compatibility posture, rights and risk posture, limitations, blocked actions, and unavailable hosted/live/download/upload/account/telemetry posture.

## Deferred

Future tasks can add active parity cases for ObjectPage, SourcePage, NeedPage, CandidatePage, snapshot, relay, terminal, native-card, print, and high-contrast projections after those dry-run fixtures exist.
