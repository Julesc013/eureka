# Rust Migration

Rust is the intended production backend lane for later. The current milestone
adds a minimal Rust workspace skeleton and parity plan only. It does not port
runtime behavior, replace Python, or start a production Rust backend.

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

The Rust migration lane is scaffolded but not operationally started. The
workspace under `crates/` contains placeholder crates only:

- `eureka-core`
- `eureka-contracts`
- `eureka-store`
- `eureka-resolver`

Current Python CLI, web, and local HTTP API behavior remain authoritative.
Python remains the executable specification, reference backend, and oracle.
Rust crates are placeholders until future parity work begins.

## Optional Check

If Rust tooling is available, run:

```powershell
cargo check --workspace --manifest-path crates/Cargo.toml
```

Normal Python verification does not require Rust tooling.
