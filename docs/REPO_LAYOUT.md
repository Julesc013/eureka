# Repo Layout

The intended bootstrap tree is:

```text
eureka/
  .aide/
  control/
  contracts/
  docs/
  runtime/
  surfaces/
  tests/
  evals/
  scripts/
  third_party/
```

## Ownership Intent

- `control/`: governance and planning assets; not runtime behavior
- `contracts/`: governed assets that define shared meaning and public boundaries
- `docs/`: founding documents, bootstrap status, and decision records
- `runtime/`: implementation areas for the engine, gateway, and connectors
- `surfaces/`: user-facing web and native applications
- `tests/`: root integration and end-to-end verification that crosses component boundaries
- `evals/`: root system and replay evaluations used to measure behavior over time
- `scripts/`: repo support scripts when lightweight automation becomes necessary
- `third_party/`: pinned or vendored external materials, kept separate from product semantics

## Test Boundary

Component-local tests live inside the component they validate, such as `runtime/engine/tests` or `surfaces/web/tests`. These should stay close to the implementation boundary they exercise.

Root `tests/` is reserved for cross-component integration and end-to-end coverage. Root `evals/` is reserved for system-level and replay-style evaluation, not unit-style component checks.

