# Parity Tests

`tests/parity/` records the plan and first Python-oracle golden outputs for
future Python-to-Rust parity checks.

Python remains the oracle. Rust Source Registry Parity Candidate v0 is the
first narrow Rust behavior seam, Rust Source Registry Parity Catch-up v0 keeps
that seam aligned with the current source inventory shape, and Rust Query
Planner Parity Candidate v0 is the second isolated candidate seam. Rust Local
Index Parity Planning v0 now records the future local-index parity lane before
any Rust index implementation starts. The implemented Rust candidates live
under `crates/eureka-core/`; the local-index lane is planning-only and is not
wired into Python runtime, web, CLI, HTTP API, workers, public-alpha paths, or
production paths.

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
- `rust_source_registry_cases.json`: compact map of current source-registry
  list/detail cases to Python-oracle golden files for the Rust source-registry
  candidate
- `RUST_LOCAL_INDEX_PARITY_PLAN.md`: planning-only local-index parity lane for
  a future Rust candidate
- `rust_local_index_cases.json`: planned local-index build/query case map
  covering current local-index goldens plus future old-platform/member/article
  query extensions
- `local_index_acceptance.schema.json`: planned machine-readable acceptance
  report shape for a future Rust local-index candidate
- `scripts/validate_rust_local_index_parity_plan.py`: stdlib validator for the
  planning artifacts; it does not require Cargo and does not run Rust
- `scripts/check_rust_source_registry_parity.py`: stdlib structure and fixture
  check for Rust Source Registry Parity Catch-up v0

Source Coverage and Capability Model v0 expands the Python source-registry
goldens with capability and coverage-depth fields. Rust Source Registry Parity
Catch-up v0 updates the isolated Rust source-registry candidate to preserve
those fields, the current connector modes, limitations, next coverage steps,
placeholder warnings, and all nine current source records. Python remains
authoritative.

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

Rust Source Registry Parity Catch-up v0 adds
`scripts/check_rust_source_registry_parity.py` as a stdlib
structure/candidate check. If Cargo is available, the script can run the
crate-local Rust source-registry tests; if Cargo is unavailable, it reports the
Cargo check as skipped while still validating the committed fixture map and
source structure. Cargo remains optional for normal Python verification.

Rust Local Index Parity Planning v0 adds a plan, fixture map, acceptance
schema, validator, and tests for the future local-index candidate. It is not a
Rust implementation. It preserves Python as oracle, leaves Rust unwired, and
requires future parity to account for source records, synthetic members,
result lanes, user-cost annotations, compatibility evidence, article/scan
records, and deterministic FTS/fallback normalization.

The Rust planner candidate is not a replacement claim. Future parity assets
should remain fixture-driven, JSON-inspectable, and explicit about allowed
divergences.
