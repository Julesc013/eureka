# Implementation Report

## Task

`INDEXLESS-LIVE-SEARCH-FALLBACK-00`

## Attachment

Implemented behind:

- `runtime/engine/resolution_runs/service.py`
- `LocalResolutionRunService._run_search`

This follows the preflight decision:

```text
DECISION: USE_EXISTING_ENGINE_RESOLUTION_RUNS_PATH
```

## What Changed

- Added `ResolutionRunFallbackPolicy` and an injected metadata-candidate fallback provider protocol to the engine run service.
- Added optional `fallback_summary` storage on `ResolutionRunRecord`.
- Serialized and loaded `fallback_summary` through the existing run store path.
- Projected optional fallback state through the resolution-runs public API and view model.
- Added focused tests for local-first behavior, miss fallback, local lookup unavailable fallback, source gates, budget gates, timeout degradation, need/candidate states, truth boundary, persistence, and public projection.

## What Did Not Change

- No canon files changed.
- No queue state changed.
- No reviewed truth path changed.
- No direct public UI-to-source fallback route was added.
- No source adapter behavior, downloads, file fetching, Wayback replay, or crawl behavior was added.

## Authority Note

`.aide/context/latest-task-packet.md` was refreshed by the required AIDE pack command. Its generic control-plane allowed paths conflict with the active user task and committed preflight, which explicitly authorize this runtime implementation. The implementation followed current repo code plus the preflight-selected runtime seam.

## Public Search Note

The existing `runtime/gateway/public_api/public_search.py` Archive.org metadata-candidate lane remains constrained and was not expanded. The new fallback implementation does not attach there; it attaches to engine resolution runs.
