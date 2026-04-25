# Rust Backend Lane

Rust is Eureka's intended production backend lane later. The current Rust
workspace is a migration skeleton only.

Python remains the executable specification, reference backend, oracle, and
fixture/eval harness. Current Python CLI, web, and local HTTP API behavior
remain authoritative until a future Rust seam passes parity tests and is
explicitly promoted.

## Current Status

- `crates/` exists as a minimal Rust workspace skeleton.
- Initial crates are documented placeholders.
- No Python runtime behavior is replaced.
- No Rust gateway, CLI, FFI, service, worker, connector, or production backend
  exists.
- No native app work is started.

## Migration Principles

- Python proves behavior first.
- Rust follows seam by seam.
- Parity tests must pass before replacement.
- No big-bang rewrite.
- No hidden divergence from Python oracle outputs.
- No production Rust service starts from this skeleton.

## Initial Crate Responsibilities

- `eureka-core`: future core object, state, representation, evidence, and
  domain types
- `eureka-contracts`: future schema-aligned contract structs
- `eureka-store`: future content-addressed and local store primitives
- `eureka-resolver`: future resolution, search, and planner logic

These crates do not implement those responsibilities yet. They only reserve the
first bounded Rust workspace shape.

## Future Crates

Future Rust work may introduce:

- `eureka-index`
- `eureka-connectors`
- `eureka-gateway`
- `eureka-cli`
- `eureka-ffi`

Those crates should appear only when their seam, oracle fixtures, and parity
criteria are explicit.

## Replacement Rule

No Rust crate replaces Python behavior until:

1. the Python oracle output for the seam is captured
2. the Rust candidate output is produced from the same fixture inputs
3. a parity comparison shows equality or an explicit allowed divergence
4. docs record what is being promoted
5. current Python tests and boundary checks still pass

Until then, Rust code is experimental scaffolding and Python remains
authoritative.
