# Master Implementation Blueprint

## Product Target

Public v1 is a read-only, evidence-first temporal artefact resolver with
reviewed local knowledge, candidate and need states, source observations,
evidence summaries, policy labels, operator review, bounded fallback, and
public surfaces generated from shared semantic contracts.

## Dependency Spine

```text
authority lock
-> public scope
-> semantic core alignment
-> resolver spine alignment
-> indexless fallback run mode
-> review ledger and reviewed-record gate
-> Workbench proof projection
-> SurfaceKernel projection
-> baseline renderer parity
-> hard-query usefulness eval
-> reviewed seed corpus
-> alpha readiness
-> alpha launch approval
-> operations hardening
-> beta
-> 1.0
```

## Existing Repo Reality

Several pieces are already implemented or specified. Future work should audit
and extend them instead of replacing them:

- `contracts/semantic/**`
- `contracts/action/action_registry.v0.json`
- `contracts/representation/**`
- `contracts/route/route_model.v0.json`
- `contracts/view/**`
- `contracts/resolution/run/**`
- `runtime/resolution_run/**`
- `runtime/engine/resolution_runs/**`
- `runtime/source/observation/**`
- `runtime/source/action/**`
- `runtime/review/**`
- `runtime/index/public/**`
- `runtime/gateway/public_api/**`
- `surfaces/web/workbench/**`
- `runtime/snapshots/**`

## Core Invariants

- Review is the truth boundary.
- Metadata is evidence, not truth.
- Source observations and candidates cannot self-promote.
- Public search remains bounded.
- Renderers and surfaces project state; they do not decide truth or policy.
- Workbench may expose operator actions but must use the same truth model.
- Public launch requires usefulness evidence, not architecture alone.

