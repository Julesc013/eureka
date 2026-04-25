# Rust Workspace Skeleton

`crates/` is Eureka's future Rust backend lane. It is intentionally not an
active backend in this milestone.

Python remains the executable specification, reference backend, and oracle.
Nothing under this workspace replaces Python runtime behavior yet.

Current crates:

- `eureka-core`: Rust Source Registry Parity Candidate v0, plus future core
  object, state, representation, evidence, and domain type scope
- `eureka-contracts`: future schema-aligned contract structs
- `eureka-store`: future content-addressed and local store primitives
- `eureka-resolver`: future resolution, search, and planner logic

Future crates may include:

- `eureka-index`
- `eureka-connectors`
- `eureka-gateway`
- `eureka-cli`
- `eureka-ffi`

The optional smoke command is:

```powershell
cargo check --workspace --manifest-path crates/Cargo.toml
cargo test --workspace --manifest-path crates/Cargo.toml
```

This command requires a local Rust toolchain. Normal Python verification does
not require Rust tooling.
