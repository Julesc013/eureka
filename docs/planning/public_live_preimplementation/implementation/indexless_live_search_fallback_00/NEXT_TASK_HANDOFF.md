# Next Task Handoff

## Recommended Next Task

`REVIEW-LEDGER-00`

## Why

Fallback can now produce candidates, needs, policy-blocked states, and degraded states on resolution runs. The next missing truth boundary is a formal review ledger for promotion, rejection, supersession, and audit.

## Inputs For Review Ledger

Review-ledger work should read:

- `runtime/engine/resolution_runs/service.py`
- `runtime/engine/interfaces/public/resolution_run.py`
- `docs/planning/public_live_preimplementation/implementation/indexless_live_search_fallback_00/POLICY_AND_SAFETY_REPORT.md`
- `docs/planning/public_live_preimplementation/architecture/REVIEW_LEDGER_SPEC.md`

## Preserve

- fallback candidates are not truth
- source observations are not truth
- public projection is not promotion
- review events are the promotion boundary

## Deferred Follow-Ups

- Wire a real approved metadata provider into the engine fallback path when repo policy chooses one.
- Align any remaining public-search candidate lane behavior with the future SurfaceKernel plan.
- Add richer run events/work-unit records if `REVIEW-LEDGER-00` or `WORKBENCH-RUN-REVIEW-PROJECTION-00` needs them.
