# Parity Tests

`tests/parity/` records the plan and first Python-oracle golden outputs for
future Python-to-Rust parity checks.

Python remains the oracle, and the Rust crates are placeholders until a later
seam has Rust candidate outputs, comparison rules, and promotion criteria.

Current assets:

- `PARITY_PLAN.md`: seam order, comparison rules, and non-goals
- `ALLOWED_DIVERGENCES.md`: future allowed-divergence record format
- `golden/python_oracle/v0/`: committed Python-oracle golden outputs

There is still no Rust parity runner in this milestone. Future parity assets
should remain fixture-driven, JSON-inspectable, and explicit about allowed
divergences.
