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

Passing those tests does not replace Python behavior. It only proves that this
isolated Rust candidate can match the committed Python-oracle fixture shape.

Source Coverage and Capability Model v0 intentionally changes the Python
source-registry oracle shape by adding capability booleans, coverage-depth
metadata, connector mode, limitations, and next coverage steps. Updating the
Rust candidate to match those fields is future Rust parity work; this source
coverage milestone does not port Rust behavior or wire Rust into runtime paths.

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

- no parity runner
- no Python runtime replacement
- no Rust behavior beyond source-registry inventory loading and public-envelope
  parity
- no Rust gateway
- no Rust CLI
- no FFI
- no native app shell
- no production service
- no replacement of Python behavior
