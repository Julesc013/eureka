# Rust Workspace Skeleton

`crates/` is Eureka's Rust parity and future migration lane. It is intentionally
not the active backend in the current baseline.

Python remains the executable specification, reference backend, and oracle.
Nothing under this workspace replaces Python runtime behavior yet.

Current crates:

- `eureka-core`: Rust Source Registry Parity Candidate v0, Rust Source Registry
  Parity Catch-up v0, and Rust Query Planner Parity Candidate v0.
- `eureka-contracts`: future schema-aligned contract structs.
- `eureka-store`: future content-addressed and local store primitives.
- `eureka-resolver`: future resolution, search, and planner logic.

Optional local smoke commands:

```powershell
cargo check --workspace --manifest-path crates/Cargo.toml
cargo test --workspace --manifest-path crates/Cargo.toml
```

These require a local Rust toolchain. Normal Python verification does not
require Rust tooling.

Python-side parity structure checks:

```powershell
python scripts/check_rust_source_registry_parity.py
python scripts/check_rust_query_planner_parity.py
```

These scripts validate committed fixture maps and source structure even when
Cargo is unavailable. They do not wire Rust into the Python runtime.
