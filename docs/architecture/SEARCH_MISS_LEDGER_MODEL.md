# Search Miss Ledger Model

Search Miss Ledger follows Query Observation in the Track B local foundry flow.
Query Observation records local query outcomes. Search Miss records classify the
gap that those outcomes suggest.

## Runtime Shape

The runtime is a small standard-library-only module. It exposes pure helpers to
build a miss from explicit input, validate the record, classify failure modes,
derive future seed candidates, preserve privacy posture, flag poisoning risks,
and summarize the result.

The module has no network, provider, browser, file-write, public-search,
runtime-state, telemetry, or master-index side effects.

## Miss Kinds

Current miss kinds include empty result, weak result, near-match only, noisy
result list, policy blocked, capability gap, source gap, extraction gap,
compatibility gap, representation gap, identity gap, temporal version gap,
ranking gap, query interpretation gap, unavailable link, unavailable external
baseline, and not evaluable.

These are local classification labels. They are not statements about the whole
source universe.

## Truth Boundary

Search miss records are review-gated learning signals. They are not public
truth, accepted evidence, accepted public records, or master-index mutations.
They cannot claim rights clearance, malware safety, verified installability, or
production readiness.

## Downstream Seeds

The runtime can prepare non-created future seed candidates for SearchNeed,
WorkUnit, and source-lead workflows. Those candidates remain review-gated and
inactive in this milestone.
