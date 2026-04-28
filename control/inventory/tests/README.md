# Test Inventory

This directory records repo-operating test and eval commands in a stable,
machine-readable form.

The registry is not a product runtime feature. It is a governance aid for
humans, AIDE-style repo operators, and Codex tasks that need to choose the
right verification lane without relying on memory.

Files:

- `test_registry.schema.json`: compact schema for individual command records.
- `test_registry.json`: inventory of important local checks, evals, smoke
  checks, Python-side parity checks, and optional Cargo commands.
- `command_matrix.json`: reusable command lanes such as `fast`, `standard`,
  `full`, `public_alpha`, `parity`, and `audit`.

Network policy:

- required lanes must stay local and deterministic
- external baseline observation remains manual unless a future accepted task
  records a human observation artifact
- optional Cargo commands require a local Rust toolchain and must not block the
  Python reference lane when Cargo is unavailable
- the Rust query-planner parity script remains a Python-side structure check
  and reports Cargo execution as skipped when the toolchain is unavailable
