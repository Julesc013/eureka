# Python To Rust Parity Plan

The Rust migration must proceed through parity, not replacement by assertion.

## Rule

Python is the oracle. Rust is the candidate. A Rust seam cannot replace Python
behavior until parity tests compare both outputs and either match exactly or
record an explicit allowed divergence.

## Comparison Model

Each future seam should define:

- Python oracle inputs
- Python oracle outputs
- Rust candidate inputs
- Rust candidate outputs
- stable JSON golden outputs
- normalization rules for non-semantic ordering or timestamp fields
- allowed divergence records
- promotion criteria

Rust Source Registry Parity Candidate v0 is the first candidate seam. Its Rust
tests compare the generated source-registry public envelopes with:

- `tests/parity/golden/python_oracle/v0/source_registry/sources_list.json`
- `tests/parity/golden/python_oracle/v0/source_registry/source_synthetic_fixtures.json`
- `tests/parity/golden/python_oracle/v0/source_registry/source_github_releases_recorded_fixtures.json`
- `tests/parity/golden/python_oracle/v0/source_registry/source_internet_archive_recorded_fixtures.json`
- `tests/parity/golden/python_oracle/v0/source_registry/source_local_bundle_fixtures.json`
- `tests/parity/golden/python_oracle/v0/source_registry/source_article_scan_recorded_fixtures.json`
- `tests/parity/golden/python_oracle/v0/source_registry/source_internet_archive_placeholder.json`
- `tests/parity/golden/python_oracle/v0/source_registry/source_local_files_placeholder.json`
- `tests/parity/golden/python_oracle/v0/source_registry/source_software_heritage_placeholder.json`
- `tests/parity/golden/python_oracle/v0/source_registry/source_wayback_memento_placeholder.json`

Passing those tests does not replace Python behavior. It only proves that this
isolated Rust candidate can match the committed Python-oracle fixture shape.

Rust Source Registry Parity Catch-up v0 updates this first seam to the current
Python source-registry shape. The candidate now models capability booleans,
coverage-depth metadata, connector mode, limitations, next coverage steps,
placeholder warnings, and the current nine-source inventory. The source cases
are listed in `tests/parity/rust_source_registry_cases.json`; the stdlib
checker `scripts/check_rust_source_registry_parity.py` validates the fixture
map and Rust source structure, and runs crate-local source-registry tests only
when Cargo is available.

Rust Query Planner Parity Candidate v0 is the second candidate seam. Its Rust
model and deterministic rules live under `crates/eureka-core/src/query_planner.rs`
and compare query-plan public envelopes with the Python-oracle
`tests/parity/golden/python_oracle/v0/query_planner/*.json` files listed in
`tests/parity/rust_query_planner_cases.json`. The candidate covers the bounded
old-platform planner families captured by the Python oracle: Windows and Mac
OS aliases, platform-as-constraint, latest-compatible release intent,
driver/hardware intent, vague software identity uncertainty, manual/document
intent, member/container discovery, article/scan intent, and generic fallback.

Passing those tests does not replace Python behavior. It proves only that this
isolated Rust candidate can match the committed Python-oracle query planner
fixture shape where Cargo is available. Normal Python verification still treats
Cargo as optional and uses the stdlib parity structure script when Rust tooling
is unavailable.

Source Coverage and Capability Model v0 intentionally changes the Python
source-registry oracle shape by adding capability booleans, coverage-depth
metadata, connector mode, limitations, and next coverage steps. Rust Source
Registry Parity Catch-up v0 now mirrors those fields in the isolated Rust
candidate without porting Python runtime behavior or wiring Rust into runtime
paths.

Old-Platform Software Planner Pack v0 intentionally changes the Python
query-planner oracle shape for selected hard old-platform queries. Future Rust
query-planner parity must reproduce platform constraints, temporal goals,
product/hardware/function hints, representation/member hints, suppression
hints, and uncertainty notes before replacement is considered.

Member-Level Synthetic Records v0 intentionally changes the Python local-index,
search, exact-resolution, and eval-visible corpus shape by adding deterministic
`synthetic_member` records for bounded local bundle fixture members. Future Rust
local-index, exact-resolution, deterministic-search, and evidence parity must
preserve member target refs, parent lineage, source/evidence summaries, member
paths, member kind, content metadata, and action hints before replacement is
considered.

Result Lanes + User-Cost Ranking v0 intentionally changes Python local-index,
deterministic-search, exact-resolution, resolution-run, and eval-visible output
by adding bounded result lanes, user-cost scores, reasons, and usefulness
summaries. Future Rust parity for local index, exact resolution, deterministic
search, and public result projection must reproduce these annotations or record
an explicit allowed divergence before replacement is considered.

Rust Local Index Parity Planning v0 records the future local-index parity lane
before any Rust index implementation starts. The plan lives in
`tests/parity/RUST_LOCAL_INDEX_PARITY_PLAN.md`, the planned case map lives in
`tests/parity/rust_local_index_cases.json`, and the planned acceptance-report
shape lives in `tests/parity/local_index_acceptance.schema.json`. The stdlib
validator `scripts/validate_rust_local_index_parity_plan.py` checks that the
plan names Python as oracle, keeps Rust unwired, references the current
local-index goldens, covers the current record kinds, and marks additional
old-platform/member/article/source-id query cases as future oracle extensions.
This is planning only: Rust Local Index parity implementation is not started.

## Golden Outputs

Rust Parity Fixture Pack v0 now commits the first Python-oracle golden outputs
under `tests/parity/golden/python_oracle/v0/`.

Golden outputs should be JSON where possible. They should be:

- generated from existing Python reference behavior
- committed only when the source fixture and command are clear
- stable enough to review in diffs
- small enough to inspect manually
- honest about unsupported or capability-gap states

Regenerate or check the current Python-oracle pack with:

```powershell
python scripts/generate_python_oracle_golden.py
python scripts/generate_python_oracle_golden.py --check
```

The v0 pack captures source registry, query planner, resolution run, local
index, resolution memory, and archive-resolution eval outputs. It normalizes
timestamps, local index paths, local index FTS mode, and generation metadata so
the committed JSON stays stable across local environments.

## Allowed Divergence Records

When Rust cannot or should not byte-match Python output, the divergence must be
explicit. A record should include:

- seam name
- fixture id or task id
- Python observed output
- Rust observed output
- reason for divergence
- owner or future review note
- decision status

No undocumented divergence should be treated as parity.

## Seam Order

The recommended migration order is:

1. source registry record loading
2. query planner
3. local index record model
4. resolution run model
5. resolution memory model
6. exact resolution
7. deterministic search
8. provenance and evidence
9. representation and access paths
10. compatibility
11. action-plan and handoff
12. acquisition, decomposition, and member access
13. local store, local index execution, and gateway projection

This order favors smaller, inspectable data contracts before broader behavior.

## Non-Goals For This Milestone

- no production parity runner
- no Python runtime replacement
- no Rust behavior beyond isolated source-registry and query-planner candidate
  parity
- no Rust gateway
- no Rust CLI
- no FFI
- no native app shell
- no production service
- no replacement of Python behavior
