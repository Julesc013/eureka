# Verification Matrix

Broad local verification was run on 2026-04-29. No network probes, external searches, browser automation, deployments, or live source calls were performed.

Summary:

- Passed commands: 81
- Failed commands: 0
- Unavailable commands: 3
- Skipped commands: 0

Unavailable commands:

- `cargo --version`: Cargo is not available in PATH.
- `cargo check --workspace --manifest-path crates/Cargo.toml`: Cargo is not available in PATH.
- `cargo test --workspace --manifest-path crates/Cargo.toml`: Cargo is not available in PATH.

Important passed lanes:

- Git status/log/diff checks.
- Unit discovery for `tests/scripts`, `tests/operations`, `tests/hardening`, `tests/parity`, `tests/evals`, `runtime`, `surfaces`, and all `tests`.
- Architecture boundary checker.
- Python oracle golden check.
- Archive resolution eval runner and JSON report.
- Search usefulness audit and JSON report.
- Publication/static/public-alpha validators.
- Static site generator and generated-data checks.
- Static host/live-backend/live-probe/compatibility/snapshot validators.
- Snapshot consumer, relay design/prototype, native, action, privacy, and WinForms planning validators.
- External baseline validation/status/list/create-template helpers.
- Rust source-registry/query-planner structure checks and Rust local-index planning validator.
- Full Project State Audit v0 validator and focused audit tests.

See `COMMAND_RESULTS.md` for command-level details.
