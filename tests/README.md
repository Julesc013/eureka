# Root Tests

`tests/` is reserved for verification that crosses component boundaries.

- `architecture/`: repo-local architectural guardrail checks and synthetic violation fixtures for the narrow boundary checker
- `evals/`: repo-level validation for shared benchmark and evaluation assets
- `integration/`: cross-component checks across contracts, runtime, and surfaces
- `parity/`: planning docs for future Python-oracle to Rust-candidate parity checks
- `end_to_end/`: higher-level product workflow checks once real behavior exists

Component-local tests stay with their owning component and should not be duplicated here.
