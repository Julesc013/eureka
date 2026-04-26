# Rust Migration

Rust is the intended production backend lane for later. The current Rust lane
has a minimal workspace, Python-oracle fixtures, and the first isolated source
registry parity candidate. It does not replace Python runtime behavior or start
a production Rust backend.

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

Source Coverage and Capability Model v0 expands the Python source-registry
oracle shape with capability and coverage-depth fields. Future Rust
source-registry parity work must learn those fields before any source-registry
replacement can be considered; this milestone does not wire Rust into Python
runtime behavior.

Real Source Coverage Pack v0 adds two more governed source records and expands
the Python-oracle source-registry and local-index goldens. Rust source-registry
parity must later account for `internet-archive-recorded-fixtures` and
`local-bundle-fixtures`, but this task does not implement Rust behavior or wire
Rust into runtime paths.

Old-Platform Software Planner Pack v0 refreshes the Python-oracle query planner
goldens with deterministic old-platform OS aliases, latest-compatible release
intent, driver/hardware intent, vague identity uncertainty, documentation
intent, member-discovery hints, and app-vs-OS-media suppression hints. Future
Rust Query Planner Parity Candidate v0 must match those Python outputs before
any planner replacement is considered.

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
10. compatibility
11. action-plan and handoff
12. acquisition, decomposition, and member access
13. local store, local index execution, and gateway projection

Each migrated seam should be checked against Python golden or parity outputs
before replacement.

## Current Status

The Rust migration lane is scaffolded and has one isolated parity candidate. The
workspace under `crates/` contains:

- `eureka-core`: Rust Source Registry Parity Candidate v0 plus future core
  placeholder scope
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
The source-registry candidate is not wired into runtime behavior. No Rust
gateway, CLI, FFI, worker, connector, production service, resolver, query
planner, local index, or memory implementation is active.

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

## Optional Check

If Rust tooling is available, run:

```powershell
cargo check --workspace --manifest-path crates/Cargo.toml
cargo test --workspace --manifest-path crates/Cargo.toml
```

Normal Python verification does not require Rust tooling.
