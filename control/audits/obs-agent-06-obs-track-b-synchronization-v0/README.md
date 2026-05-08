# OBS-AGENT-06 - OBS and Track B Synchronization

## What Was Added

- OBS/Track B synchronization policy.
- Read-only synchronization matrix.
- Handoff readiness inventory.
- Audit, validation, and summary scripts.
- Handoff summary, gap register, dependency map, source policy items, human review items, and next actions.
- Operation tests for the sync audit lane.

## Why Sync Is Needed

OBS has generated review-gated candidates, SearchNeed seeds, and WorkUnit seeds. Track B has advanced through node, policy, capability, WorkUnit, WorkUnit result, and local foundry state contracts. The sync audit records how those outputs align without mutating Track B or activating runtime behavior.

## What Was Inspected

- OBS-REPLAN-01 and OBS-AGENT-01 through OBS-AGENT-05 artifacts.
- Track B audit reports through TRACK-B-06.
- Track B node, policy, capability, WorkUnit, WorkUnit result, and local foundry state contracts.
- OBS candidate, review queue, SearchNeed seed, and WorkUnit seed inventories.

## What Remains Blocked

- Runtime SearchNeed consumption.
- Runtime WorkUnit creation or execution.
- Source access approval.
- Public index effects.
- Evidence acceptance.
- Master-index mutation.

## Parallel Continuation

The OBS side lane can proceed to human review packet preparation. Track B can proceed independently to TRACK-B-07. The OBS lane must not overwrite Track B queue or runtime state.

## Validation Commands

```text
python scripts/audit_obs_track_b_synchronization.py --list-inputs
python scripts/audit_obs_track_b_synchronization.py --check
python scripts/validate_obs_track_b_synchronization.py
python scripts/summarize_obs_track_b_handoff.py
python -m unittest tests.operations.test_obs_track_b_synchronization
```

## No-Goals

- No external observation.
- No browser, API, provider, model, scrape, or crawl.
- No Track B mutation.
- No runtime SearchNeed or WorkUnit creation.
- No WorkUnit execution.
- No source approval.
- No accepted evidence truth.
- No master-index mutation.

## Next Task

- `OBS-AGENT-07 - Human review packet for OBS candidates`
