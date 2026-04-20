# Archive Fixtures

This directory holds governed fixture material used to exercise archive contracts.

Current scope is intentionally small:

- synthetic, rights-safe local fixtures only
- deterministic inputs for bootstrap runtime, gateway, and web-surface slices
- consumed through a local synthetic connector path during bootstrap
- small enough to inspect manually while still supporting exact resolution, deterministic search, and honest absence behavior
- no external acquisition and no real archive corpus

These fixtures support inspection and harness-oriented testing. They do not settle broader connector, trust, or provenance strategy.
