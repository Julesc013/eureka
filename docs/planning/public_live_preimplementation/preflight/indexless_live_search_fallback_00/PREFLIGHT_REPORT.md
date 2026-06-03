# Preflight Report

## Scope

Task ID: `INDEXLESS-LIVE-SEARCH-FALLBACK-00-PREFLIGHT`

Goal: determine whether indexless live search fallback can be implemented as a
resolver/run mode using existing repo seams without creating a parallel
UI-to-source path.

This report is based on focused repo inspection. It does not run full test
discovery and does not mutate protected product paths.

## Required Reading Status

Read or inspected:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `docs/planning/public_live_preimplementation/**`
- focused `contracts/**`, `runtime/**`, `surfaces/**`, `tests/**`

Missing optional requested files:

- `.aide/queue/current.toml`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`

The missing optional files do not block this preflight because current checked
in code, queue index, AGENTS guidance, and committed planning docs provide
enough authority for a bounded decision.

## Repo Authority Facts

- The repo is bootstrap/pre-product and must preserve component boundaries.
- Runtime behavior belongs under `runtime/**`; gateway/public APIs project
  bounded responses and must not own source truth.
- Contracts own meaning, but this task may not modify `contracts/**`.
- Public alpha remains read-only and public source fanout remains disabled.
- Review remains the truth boundary.
- Existing planning docs are advisory relative to checked-in code.

## Queue Facts

- `.aide/queue/index.yaml` identifies `INDEXLESS-LIVE-SEARCH-FALLBACK-00` as
  the current recommended product task.
- `.aide/queue/current.toml` is absent.
- Queue state was not modified.

## Summary Of Findings

- `runtime/engine/resolution_runs/service.py` is the current persistent run
  service. It owns run IDs, checked source summaries, deterministic search
  execution, absence reports, and local run persistence.
- `runtime/resolution_run/**` is a useful dry-run kernel with policy/event and
  WorkUnit concepts, but it is in-memory and explicitly blocks live source
  behavior.
- `runtime/source/action/**`, `runtime/source/observation/**`, and
  `runtime/source/observation/archive_org_public_metadata.py` already contain
  source observation, candidate, budget, and policy concepts that can be reused
  or wrapped.
- `runtime/gateway/public_api/public_search.py` already has an optional
  Archive.org candidate provider hook. This is bounded and review-only, but it
  is too close to the forbidden path if expanded as the main fallback attach
  point.
- Existing public surfaces and snapshot/read-only APIs contain strong blockers
  for downloads, installs, uploads, live probes, local paths, and arbitrary
  URLs.

## Primary Decision

Use the current engine resolution-runs path:

```text
DECISION: USE_EXISTING_ENGINE_RESOLUTION_RUNS_PATH
```

## Warnings

- The engine `ResolutionRunRecord` does not yet carry explicit WorkUnits,
  RunEvents, fallback status, source observations, or candidate/need lanes.
- Canonical status and affordance contracts exist as schema shapes but do not
  yet enumerate every public-live status or action.
- `public_search.py` can directly invoke an Archive.org candidate provider when
  configured. The implementation task must not make that surface hook the
  authoritative fallback path.
- Explicit fallback disable, source-family disable, and review freeze switches
  are partial across the repo and should be normalized in the fallback task or
  the next semantic-core/review-ledger task.

## Next Task Recommendation

Proceed to `INDEXLESS-LIVE-SEARCH-FALLBACK-00` with the selected engine
resolution-runs path. Run `SEMANTIC-CORE-CONTRACTS-00` only if implementation
cannot map fallback output to existing candidate/need/policy-blocked/unavailable
states without changing live contracts.
