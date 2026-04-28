# Parity Tests

`tests/parity/` records the plan and first Python-oracle golden outputs for
future Python-to-Rust parity checks.

Python remains the oracle. Rust Source Registry Parity Candidate v0 is the
first narrow Rust behavior seam, and Rust Query Planner Parity Candidate v0 is
the second isolated candidate seam. Both live under `crates/eureka-core/` and
are not wired into Python runtime, web, CLI, HTTP API, workers, public-alpha
paths, or production paths.

Current assets:

- `PARITY_PLAN.md`: seam order, comparison rules, and non-goals
- `ALLOWED_DIVERGENCES.md`: future allowed-divergence record format
- `golden/python_oracle/v0/`: committed Python-oracle golden outputs
- `crates/eureka-core/src/source_registry.rs`: first Rust source-registry
  candidate compared against the Python-oracle source-registry goldens
- `crates/eureka-core/src/query_planner.rs`: isolated Rust deterministic
  query-planner candidate compared against Python-oracle query-planner goldens
- `rust_query_planner_cases.json`: compact map of query inputs to Python-oracle
  golden files for the Rust planner candidate

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

Result Lanes + User-Cost Ranking v0 refreshes Python-oracle resolution-run,
local-index, and archive-resolution eval goldens with deterministic result
lanes, user-cost scores, reasons, and usefulness summaries. Future Rust
local-index, deterministic-search, exact-resolution, and result-projection
parity must account for these bounded annotations before any replacement claim;
no Rust behavior is implemented or wired in here.

Compatibility Evidence Pack v0 refreshes Python-oracle local-index,
resolution-run, and archive-resolution eval goldens with source-backed
compatibility evidence records and summaries for current fixture-backed
records. Future Rust planner/index/compatibility parity must account for this
shape before any replacement claim; no Rust behavior is implemented or wired in
here.

Rust Query Planner Parity Candidate v0 adds
`scripts/check_rust_query_planner_parity.py` as a stdlib structure/candidate
check. If Cargo is available, the script can run the crate-local Rust
query-planner tests; if Cargo is unavailable, it reports the Cargo check as
skipped while still validating the committed fixture map and source structure.
Cargo remains optional for normal Python verification.

The Rust planner candidate is not a replacement claim. Future parity assets
should remain fixture-driven, JSON-inspectable, and explicit about allowed
divergences.
