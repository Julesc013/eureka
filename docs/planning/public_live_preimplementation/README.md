# Public Live Preimplementation Package

Task: `EUREKA-PUBLIC-LIVE-PREIMPLEMENTATION-MEGA-00`

Status: planning package. This tree is not canon, not live contract authority,
and not runtime implementation. It reconciles the public-live roadmap with the
current repository state so future implementation can start without adding a
parallel product path.

## Controlling Decision

Eureka should move toward public-live work as one governed semantic resolver
spine:

```text
query
-> reviewed local knowledge
-> unresolved state if insufficient
-> ResolutionRunKernel
-> WorkUnits
-> SourceObservations
-> EvidenceCandidates or SearchNeeds
-> ReviewLedger
-> ReviewedRecords
-> IndexBuilder
-> SurfaceKernel
-> public/API/text/snapshot/Workbench projections
```

Public launch remains gated. Existing public-alpha read-only and deploy-dry-run
evidence is preserved, but later reassessment and queue state identify
indexless fallback, usefulness evaluation, and reviewed artifact record gates as
current blockers.

## How To Use This Package

1. Start with `IMPLEMENTATION_START_RECOMMENDATION.md`.
2. Check current authority in `authority/AUTHORITY_LOCK.md`.
3. Use `EXECUTION_QUEUE.md` and `QUEUE_DAG.yml` to pick the next bounded task.
4. Use `tasks/*.md` as task prompts.
5. Keep implementation edits outside this planning tree and inside the
   component boundaries named in `MODULE_BOUNDARIES.md`.

## Non-Claims

This package does not claim public launch, production readiness, public live
source fanout, downloads, extraction, model/provider use, rights clearance,
malware safety, broad corpus coverage, or reviewed truth creation.

