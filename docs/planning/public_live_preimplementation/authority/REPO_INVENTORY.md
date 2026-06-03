# Repo Inventory

This inventory is intentionally summarized. It records capability presence
without claiming maturity.

## Existing Roots

- `.aide/`: repo operating metadata and compact task context.
- `control/`: inventories, policies, audits.
- `contracts/`: semantic, route, action, representation, view, source,
  review, search, snapshot, hosting, and runtime contracts.
- `runtime/`: Python reference runtime including resolver, gateway, source,
  review, index, snapshot, hosting, and local paths.
- `surfaces/`: web Workbench, web server, API, CLI projections.
- `site/`: site output/source area, not modified by this task.
- `snapshots/`: snapshot schemas and examples.
- `examples/`: public-safe fixtures and examples.
- `evals/`: archive resolution and search usefulness eval structures.
- `tests/`: focused contract, runtime, operation, hosting, public-alpha,
  surface, and connector tests.
- `release/`: hosting and release planning artifacts.

## Relevant Existing Files

- `contracts/semantic/status.v0.json`
- `contracts/semantic/affordance.v0.json`
- `contracts/action/action_registry.v0.json`
- `contracts/representation/*.v0.json`
- `contracts/route/route_model.v0.json`
- `contracts/resolution/run/*.v0.json`
- `contracts/source/action/source_observation_envelope.v0.json`
- `contracts/runtime/evidence_candidate.v0.json`
- `contracts/query/search_need_record.v0.json`
- `contracts/stores/review_event.v0.json`
- `contracts/view/**`
- `runtime/resolution_run/**`
- `runtime/engine/resolution_runs/**`
- `runtime/source/observation/**`
- `runtime/source/action/**`
- `runtime/review/**`
- `runtime/index/public/**`
- `runtime/gateway/public_api/public_alpha_readonly.py`
- `surfaces/web/workbench/**`

## Inventory Caveat

Presence is not acceptance for the next implementation. The preflight task must
identify which parallel-looking paths are authoritative.

