# Next Task Handoff

## Recommended Next Task

`WORKBENCH-RUN-REVIEW-PROJECTION-00`

## Why

The review ledger can now record canonical decisions and audit context, but operators still need a Workbench proof surface to inspect runs, fallback outputs, source observations, review items, decisions, and review/index handoff state together.

## Inputs

Read:

- `runtime/review/ledger.py`
- `runtime/review/queue/**`
- `runtime/engine/resolution_runs/service.py`
- `docs/planning/public_live_preimplementation/implementation/review_ledger_00/**`
- `docs/planning/public_live_preimplementation/architecture/WORKBENCH_RUN_REVIEW_PROJECTION_SPEC.md`

## Preserve

- public surfaces remain read-only
- review ledger remains the promotion boundary
- Workbench projection does not create truth by itself
- reviewed/public index rebuild remains explicit and auditable
