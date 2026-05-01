# Allowed And Forbidden Roots

Committed report-like files are allowed only for synthetic examples,
audit-safe milestone evidence, hand-authored docs, or synthetic test fixtures.

Allowed committed roots:

- `control/audits/*`
- `examples/import_reports/`
- `docs/` for hand-authored docs only
- `tests/fixtures/` for synthetic test fixtures

Future local/private roots:

- `.eureka-local/reports/`
- `.eureka-local/staging/`
- `.eureka-local/quarantine/`
- `.eureka-local/import-reports/`
- `.eureka-reports/`
- app-local native roots
- user-configured roots outside the repo
- test temp directories

Forbidden roots for local/private report output include `site/`, `site/dist/`,
`external/`, `runtime/`, `surfaces/`, `control/inventory/`, `contracts/`,
`docs/` except hand-authored docs, `snapshots/examples/`, `evals/`, `crates/`,
`.github/`, `.aide/` except deliberate metadata, and canonical source trees.
