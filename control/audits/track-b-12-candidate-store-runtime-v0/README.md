# TRACK-B-12 Candidate Store Runtime

This audit pack records the first bounded Candidate Store runtime for Track B.

## Added

- `runtime/local/foundry/candidate_store.py`
- `scripts/record_candidate.py`
- `scripts/summarize_candidate_store.py`
- `scripts/validate_candidate_store_runtime.py`
- candidate status, type, origin, output, review, dedup, and runtime policies
- candidate examples under `examples/index/candidates/`
- generated sample candidate store snapshot and summary
- reference, architecture, and review documentation

## Why This Follows Node Policy Evaluation

The node policy evaluator determines whether WorkUnits and node scopes are
allowed, blocked, gated, or deferred. Candidate store runtime preserves the
resulting provisional discoveries as reviewable candidate records without
executing WorkUnits or accepting truth.

## What Remains Forbidden

- accepted public records
- accepted evidence truth
- master-index mutation
- local private state creation
- network, API, browser, model, provider, or live-source calls
- source sync, live probes, scraping, crawling, downloads, uploads, accounts,
  telemetry, native projects, hosted runtime, or review runtime
- automatic merge, deduplication, promotion, or public export

## Next Task

TRACK-B-13 - Local source cache runtime planning.

