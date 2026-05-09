# OBS Track B Synchronization

## Purpose

OBS and Track B run in parallel so observation-side candidate discovery can continue while Track B defines node, WorkUnit, result, and local-state contracts. Synchronization is the read-only audit that compares those lanes and records what can be reviewed later.

The sync audit does not promote anything. It produces a matrix, readiness summary, gap register, and next-action notes.

## Allowed Inputs

- OBS audit packs from OBS-REPLAN-01 and OBS-AGENT-01 through OBS-AGENT-05.
- OBS inventories for candidates, review queues, SearchNeed seeds, and WorkUnit seeds.
- Track B audit packs and contracts under `contracts/node/`.
- Track B node inventories and reference docs.
- Repo-local validation scripts and reports.

All inputs are repo-local. The audit does not use live external sources, browser sessions, APIs, provider/model calls, scraping, crawling, downloads, uploads, accounts, or telemetry.

## What OBS Can Feed Track B

- Observation candidates can feed human review packets.
- Source gap candidates can feed source policy decision packets.
- SearchNeed seeds can feed future Track B SearchNeed planning after review.
- WorkUnit seeds can feed future Track B WorkUnit planning after review.
- Manual observation pending slots can feed future manual observation work.

Each item remains a draft until a future reviewed Track B flow accepts it.

## Track B Requirements

Track B must define and validate the structure, execution, review, result handling, local state handling, and promotion gates before OBS outputs can become runtime records. Contract presence is useful for alignment, but it is not runtime activation.

SearchNeed seeds are not runtime SearchNeeds. WorkUnit seeds are not executable WorkUnits.

## Review Gates

Human review is required when downstream use is proposed. Source policy review is required before any live source access or source connector planning can move beyond a draft. Evidence review is required before any result can become accepted evidence truth.

## Runtime and Public Effects

Runtime activation is not allowed by this audit. Public index effects are not allowed by this audit. The master index is not mutated.

## Validation

Use:

```text
python scripts/audit_obs_track_b_synchronization.py --list-inputs
python scripts/audit_obs_track_b_synchronization.py --check
python scripts/validate_obs_track_b_synchronization.py
python scripts/summarize_obs_track_b_handoff.py
```

Run broader repo checks as the task requires, then record warnings honestly.

## No-Goals

- No Track B mutation.
- No runtime SearchNeed creation.
- No runtime WorkUnit creation.
- No WorkUnit execution.
- No source approval.
- No observed baseline creation.
- No accepted evidence truth.
- No master-index mutation.
- No live external access, browser use, API calls, scraping, crawling, downloads, uploads, accounts, or telemetry.
