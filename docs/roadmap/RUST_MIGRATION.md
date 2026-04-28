# Rust Migration

Rust is the intended production backend lane for later. The current Rust lane
has a minimal workspace, Python-oracle fixtures, the first isolated source
registry parity candidate, the Rust source-registry catch-up to the current
Python source shape, the first isolated query-planner candidate, and a
planning-only Rust Local Index parity lane. It does not replace Python runtime
behavior or start a production Rust backend.

## Language Policy

- Rust: future production backend and shared core
- Python: reference backend, oracle, tooling, migration harness, fixture and
  eval support
- SQL: first-class storage, index, and query layer
- TypeScript: progressive web enhancement later
- Swift: Apple-native shell later
- C# or C++: Windows-native shell later
- C or C89: legacy or survival utilities and ABI shims only

## Migration Rule

The migration rule should be:

```text
Python proves behavior.
Rust becomes production implementation later.
Parity tests protect the transition.
```

No big-bang rewrite is accepted. Every Rust migration step must be seam-sized
and parity-tested against Python oracle outputs before replacement.

Rust Parity Fixture Pack v0 now captures the first committed Python-oracle
golden outputs under `tests/parity/golden/python_oracle/v0/`. Future Rust
candidate seams must match those outputs, or record an explicit allowed
divergence, before replacing any Python behavior.

Rust Source Registry Parity Candidate v0 is the first such candidate. It loads
the governed source inventory and compares source-registry public envelopes
against the committed Python-oracle source-registry goldens.

Rust Source Registry Parity Catch-up v0 updates that first candidate to the
current Python source-registry shape, including capability booleans,
coverage-depth metadata, connector mode, current limitations, next coverage
step, placeholder warnings, and all nine current source records. It keeps
Python as oracle and leaves Rust unwired from runtime, web, CLI, HTTP API,
workers, public-alpha, and production paths.

Rust Query Planner Parity Candidate v0 is the second isolated candidate. It
adds a deterministic Rust query-planner model and rule set in `eureka-core`,
expands the Python-oracle query-planner golden set, and records a compact case
map for old-platform planner parity. It is not wired into Python runtime, web,
CLI, HTTP API, workers, public-alpha paths, or production behavior.

Source Coverage and Capability Model v0 expands the Python source-registry
oracle shape with capability and coverage-depth fields. Real Source Coverage
Pack v0, Article/Scan Fixture Pack v0, and old-platform fixture expansions add
recorded fixture and placeholder records. Rust Source Registry Parity Catch-up
v0 now accounts for those source-registry fields and records in the isolated
candidate without implementing Rust runtime behavior.

Old-Platform Software Planner Pack v0 refreshes the Python-oracle query planner
goldens with deterministic old-platform OS aliases, latest-compatible release
intent, driver/hardware intent, vague identity uncertainty, documentation
intent, member-discovery hints, and app-vs-OS-media suppression hints. Rust
Query Planner Parity Candidate v0 now targets those Python outputs as an
isolated candidate; matching them still does not promote Rust into active
planner runtime.

Member-Level Synthetic Records v0, Result Lanes + User-Cost Ranking v0, and
Compatibility Evidence Pack v0 further refresh the Python-oracle local-index,
resolution-run, search, compatibility, and eval-visible outputs with member
records, lane/user-cost annotations, and source-backed compatibility evidence.
Future Rust local-index, deterministic-search, exact-resolution,
compatibility, and result-projection parity must match those shapes or record
explicit allowed divergences before any replacement is considered.

Rust Local Index Parity Planning v0 now adds the planning artifacts for that
future candidate: `tests/parity/RUST_LOCAL_INDEX_PARITY_PLAN.md`,
`tests/parity/rust_local_index_cases.json`,
`tests/parity/local_index_acceptance.schema.json`, and
`scripts/validate_rust_local_index_parity_plan.py`. This is planning only.
Rust Local Index parity implementation is not started, Python remains the
oracle, and Rust remains unwired from runtime and surfaces.

## Suggested Future Layout

```text
crates/
  Cargo.toml
  eureka-core/
  eureka-contracts/
  eureka-store/
  eureka-resolver/
  eureka-index/
  eureka-connectors/
  eureka-gateway/
  eureka-cli/
  eureka-ffi/

python/
  oracle/
  tooling/
  migrations/

tests/
  parity/
```

## Migration Sequence

When migration begins, the order should be seam-oriented:

1. source registry record loading
2. query planner
3. local index record model
4. resolution run model
5. resolution memory model
6. exact resolution
7. deterministic search
8. provenance and evidence
9. representation and access paths
10. result lanes and user-cost annotations
11. compatibility
12. action-plan and handoff
13. acquisition, decomposition, and member access
14. local store, local index execution, and gateway projection

Each migrated seam should be checked against Python golden or parity outputs
before replacement.

## Current Status

The Rust migration lane is scaffolded and has two isolated parity candidates,
with the source-registry candidate caught up to the current Python source
inventory shape, plus a planning-only local-index parity lane.
The workspace under `crates/` contains:

- `eureka-core`: Rust Source Registry Parity Candidate v0, Rust Query Planner
  Parity Candidate v0, plus future core placeholder scope; no Rust local-index
  implementation is present
- `eureka-contracts`: placeholder
- `eureka-store`: placeholder
- `eureka-resolver`: placeholder

The first Python-oracle golden fixture pack exists for:

- source registry
- query planner
- resolution runs
- local index
- resolution memory
- archive-resolution eval runner

Current Python CLI, web, and local HTTP API behavior remain authoritative.
Python remains the executable specification, reference backend, and oracle.
The source-registry and query-planner candidates are not wired into runtime
behavior. No Rust gateway, CLI, FFI, worker, connector, production service,
resolver, runtime query planner, local index, or memory implementation is
active.

Rust Local Index Parity Planning v0 targets the current Python-oracle
local-index goldens, including the 489-record bounded build status and the
current `synthetic`, `archive`, and no-result query outputs. Additional
old-platform, member, article/scan, and source-id query cases are explicitly
marked as future Python-oracle extensions before a Rust candidate begins.

## Python Oracle Fixture Pack

Use the stdlib generator to refresh or verify the committed v0 pack:

```powershell
python scripts/generate_python_oracle_golden.py
python scripts/generate_python_oracle_golden.py --check
```

The generator normalizes unstable fields such as timestamps, local index paths,
SQLite FTS mode, and generation metadata. It preserves semantically meaningful
fields, including the current archive-resolution eval capability gaps and
source-backed not-satisfied cases.
Result Lanes + User-Cost Ranking v0 intentionally adds lane and user-cost fields
to Python oracle outputs for current result records. Compatibility Evidence
Pack v0 intentionally adds source-backed compatibility evidence fields where
current fixture records support them. Future Rust local-index,
deterministic-search, exact-resolution, compatibility, and public-projection
parity must match those bounded annotations or record explicit allowed
divergences before any replacement claim.

## Optional Check

If Rust tooling is available, run:

```powershell
cargo check --workspace --manifest-path crates/Cargo.toml
cargo test --workspace --manifest-path crates/Cargo.toml
```

Normal Python verification does not require Rust tooling.

Rust Source Registry Parity Catch-up v0 and Rust Query Planner Parity
Candidate v0 provide stdlib parity structure checks. Rust Local Index Parity
Planning v0 adds a planning validator:

```powershell
python scripts/check_rust_source_registry_parity.py
python scripts/check_rust_source_registry_parity.py --json
python scripts/check_rust_query_planner_parity.py
python scripts/check_rust_query_planner_parity.py --json
python scripts/validate_rust_local_index_parity_plan.py
python scripts/validate_rust_local_index_parity_plan.py --json
```

These commands validate fixture maps and Rust candidate structure with the
Python standard library. If Cargo is installed, the scripts also run the
crate-local Rust candidate tests; otherwise they report Cargo as skipped.

## Rust Checkpoint

Post-Queue State Checkpoint v0 records the current post-queue evidence and
verification state under `control/audits/post-queue-state-checkpoint-v0/`. It
is audit/reporting only; it does not add backend hosting, live probes,
production deployment, Rust runtime wiring, relay services, or native app
projects.
