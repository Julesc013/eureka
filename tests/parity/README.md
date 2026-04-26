# Parity Tests

`tests/parity/` records the plan and first Python-oracle golden outputs for
future Python-to-Rust parity checks.

Python remains the oracle. Rust Source Registry Parity Candidate v0 is the
first narrow Rust behavior seam, and it is isolated under `crates/eureka-core/`.
It is not wired into Python runtime, web, CLI, HTTP API, workers, or production
paths.

Current assets:

- `PARITY_PLAN.md`: seam order, comparison rules, and non-goals
- `ALLOWED_DIVERGENCES.md`: future allowed-divergence record format
- `golden/python_oracle/v0/`: committed Python-oracle golden outputs
- `crates/eureka-core/src/source_registry.rs`: first Rust source-registry
  candidate compared against the Python-oracle source-registry goldens

Source Coverage and Capability Model v0 expands the Python source-registry
goldens with capability and coverage-depth fields. The Rust source-registry
candidate must be updated in a later Rust parity task before it can claim
current source-registry parity again; Python remains authoritative.

Real Source Coverage Pack v0 expands the Python-oracle source-registry and
local-index goldens with `internet-archive-recorded-fixtures` and
`local-bundle-fixtures`. Rust remains a future parity lane only; no Rust
runtime behavior is introduced by those fixture updates.

Old-Platform Software Planner Pack v0 refreshes Python-oracle query-planner,
planned-run, resolution-memory, and archive-resolution eval goldens. Future
Rust Query Planner Parity Candidate v0 must target these outputs; no Rust
planner behavior is implemented or wired in here.

Member-Level Synthetic Records v0 refreshes Python-oracle local-index,
resolution, search, memory, and eval goldens with deterministic
`synthetic_member` records from committed local bundle fixtures. Future Rust
local-index or exact-resolution parity work must learn this member record shape
before any replacement claim; no Rust behavior is implemented or wired in here.

There is still no Rust parity runner in this milestone. Future parity assets
should remain fixture-driven, JSON-inspectable, and explicit about allowed
divergences.
