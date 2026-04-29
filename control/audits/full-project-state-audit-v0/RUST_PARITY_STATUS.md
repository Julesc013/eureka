# Rust Parity Status

Rust is present as isolated parity candidate/planning work only. Python remains the oracle and runtime reference.

Verified locally without Cargo:

- Python oracle golden check passed; file count: 40.
- Rust source-registry parity script passed structure checks.
- Rust source-registry parity source count: 9.
- Rust source-registry case count: 10.
- Rust query-planner parity script passed structure checks.
- Rust query-planner case count: 16.
- Rust local-index parity planning validator passed.
- Rust local-index parity cases: 15 total; 3 current-oracle query cases; 12 planned future query cases; 7 record kinds.

Unavailable:

- `cargo --version`
- `cargo check --workspace --manifest-path crates/Cargo.toml`
- `cargo test --workspace --manifest-path crates/Cargo.toml`

Runtime wiring status:

- Rust is not called by Python runtime, web, CLI, HTTP API, workers, public-alpha wrapper, publication surfaces, relay, or native clients.

Next Rust action:

- Cargo/toolchain setup and review are human/operator work.
- Rust Local Index Parity Candidate v0 should wait for planning review and Cargo availability.
