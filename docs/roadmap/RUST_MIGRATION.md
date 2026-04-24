# Rust Migration

Rust is the intended production backend lane for later. It is not the current
implementation task.

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

## Suggested Future Layout

```text
crates/
  eureka-core/
  eureka-contracts/
  eureka-connectors/
  eureka-resolver/
  eureka-store/
  eureka-index/
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

1. contracts and shared types
2. canonical records and store logic
3. resolver and search behavior
4. connector support
5. gateway and CLI

Each migrated seam should be checked against Python golden or parity outputs
before replacement.

## Current Status

The Rust migration is planned but not started. Source Registry v0 now exists in
the Python reference lane, but no Rust workspace or crates should be introduced
until later backend milestones, parity expectations, and migration boundaries
are clearer.
