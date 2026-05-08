# SearchNeed Model

SearchNeed follows Query Observation and Search Miss Ledger in the Track B
local foundry flow. Query Observation records a local query outcome. Search
Miss Ledger classifies the gap. SearchNeed turns that reviewed gap shape into a
reusable unresolved-search object.

## Runtime Shape

The runtime is a small standard-library-only module. It exposes pure helpers to
build a need from explicit input, validate the record, classify intent, derive
future seed candidates, preserve privacy posture, flag poisoning risks, detect
absence overclaims, and summarize the result.

The module has no network, provider, browser, file-write, public-search,
WorkUnit execution, runtime-state, telemetry, or master-index side effects.

## Record Shape

A SearchNeed records a stable need id, status, intent, label, canonical key,
query summary, interpreted intent, object family, topic, version or state,
platform or context, artifact type, desired user action, aliases, demand
summary, gap summaries, absence scope, review gates, privacy posture, poisoning
posture, truth boundary, product boundary, limitations, and notes.

## Truth Boundary

SearchNeed records are review-gated planning objects. They are not public truth,
accepted evidence, accepted public records, or master-index mutations. They
cannot claim rights clearance, malware safety, verified installability,
production readiness, or universe-level absence.

## Downstream Seeds

The runtime can prepare non-created future seed candidates for WorkUnit,
source-lead, and candidate-review workflows. Those candidates remain
review-gated and inactive in this milestone.
