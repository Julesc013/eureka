# Resolver Spine Spec

## Purpose

Unify public search, Workbench, fallback, source observations, review, index,
snapshots, and renderers behind one resolver spine.

## Spine

```text
SearchRequest
-> reviewed local lookup
-> ResolutionRun
-> WorkUnit
-> SourceObservation
-> EvidenceCandidate or SearchNeed
-> ReviewEvent
-> ReviewedRecord
-> IndexBuild
-> ViewModel
-> Representation
```

## Existing Paths To Audit

- `runtime/resolution_run/**`
- `runtime/engine/resolution_runs/**`
- `runtime/source/observation/**`
- `runtime/source/action/**`
- `runtime/review/**`
- `runtime/index/public/**`
- `runtime/gateway/public_api/**`

## Non-Goals

No new runtime root, no public live fanout, no direct UI-to-source path, no
reviewed truth mutation outside review.

