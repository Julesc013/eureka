# Local Worker and Task Model v0

`runtime/engine/workers/` holds Eureka's first deterministic local task execution
substrate.

This slice is intentionally narrow:

- synchronous only
- caller-provided local task-store root
- JSON persistence only
- stdlib-only
- no retries, priorities, cancellation, checkpoints, or background scheduling
- no distributed queue semantics

Supported task kinds in v0:

- `validate_source_registry`
- `build_local_index`
- `query_local_index`
- `validate_archive_resolution_evals`

The runtime here wraps existing bounded engine behavior. It does not replace
direct commands, introduce orchestration semantics, or imply future queue
behavior has already landed.
