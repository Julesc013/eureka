# Dev To Main Promotion Gate Status

## Status

```text
DEV_TO_MAIN_PROMOTION_BLOCKED
```

## Gate Matrix

| Gate | Status | Evidence |
|---|---|---|
| Full discovery current | PASS | Summary `HEAD` matches current `HEAD`. |
| Full discovery green | FAIL | External run status is `fail`. |
| Queue state consistent | FAIL | Queue handoff drift is the largest failure family. |
| README/current docs synchronized | NOT_EVALUATED_IN_THIS_TASK | No docs reconciliation was performed. |
| No protected path drift | NOT_EVALUATED_IN_THIS_TASK | Ingest did not run protected-path drift repair. |
| No generated artifact drift | FAIL | Forbidden output root failure is present. |
| Promotion review packet exists | NOT_EVALUATED_IN_THIS_TASK | Promotion review is not the current task. |
| Manual approval exists | MISSING | No promotion approval exists. |

## Decision

Do not promote `dev` to `main`.
