# Repo Layout

Eureka's active bootstrap tree is governed by `contracts/repo/*` and the
component boundaries in `AGENTS.md`.

```text
eureka/
  .aide/                  repo-local automation metadata
  .aide.local.example/    committed local-state template
  .github/                repository automation
  control/                governance, inventories, audits, policies, evidence
  contracts/              schemas, contracts, packets, and public authority
    repo/                 repository structure canon
    control_schemas/      migrated schema authority formerly under control
                         (known taxonomy debt; see path taxonomy policy)
  runtime/                Python reference runtime
    engine/               current engine/kernel boundary
    gateway/              gateway runtime behavior
    connectors/           bounded source acquisition adapters
  surfaces/               user-facing projections and adapters
    api/                  API projection notes; runtime service stays in gateway
    cli/                  current local stdlib CLI surface
    files/                static files projection notes
    lite/                 lightweight static projection notes
    native/               native projection adapters, not native project authority
    text/                 plain-text static projection notes
    web/
      server/
      workbench/
        local_html/       server-rendered local workbench presentation
  site/                   static site source and generated public artifact
    assets/
    data/
    pages/
    templates/
    dist/
      data/public_index/  committed generated public-index artifact
  snapshots/
    examples/
    schema/
  native/                 canonical native client project root
  crates/                 Rust parity and future production-lane experiments
  docs/                   human documentation
  evals/                  system and replay evaluations
  examples/               public-safe examples and fixtures
  tools/                  substantive repo tooling implementations
    validators/
    generators/
    auditors/
    reporters/
    migrations/
    release/
  scripts/                thin compatibility wrappers and command entry points
  release/                release and deployment definitions
    hosting/
      render/
  external/               pinned outside references
  archive/                retired, quarantined, or historical material
    prototypes/
```

## Ownership Intent

- `control/`: governance and planning assets; not runtime behavior or schema authority.
- `contracts/`: governed assets that define shared meaning and public boundaries.
- `runtime/`: engine, gateway, connector, store, and local-service implementation.
- `surfaces/`: user-facing projections over runtime and contract packets.
- `site/`: static site inputs plus inventoried generated/public artifacts.
- `tools/`: implementation for validators, generators, auditors, reporters, migrations, and release helpers.
- `scripts/`: stable command paths that wrap `tools/` implementations.
- `release/`: deployment and packaging definitions; no generated release output.
- `archive/`: retained historical material that is not active source authority.

## Second-Level Taxonomy

`control/policies/path_taxonomy_policy.json` and
`scripts/validate_path_taxonomy.py` record the current allowed surface families,
the remaining contracts/runtime/examples taxonomy debt, and forbidden active
paths such as `release/render` and `surfaces/native/cli`.

`control/policies/taxonomy_closeout_policy.json`,
`control/policies/aide_ledger_size_policy.json`, and
`scripts/validate_taxonomy_closeout_policy.py` record the targeted closeout
decision after the root cleanup:

- Runtime flat names are frozen compatibility paths until family-by-family
  migration.
- Contract family moves are migration-map-first, with `contracts/control_schemas`
  classified as a compatibility authority path.
- Examples stay public-safe fixtures and move only through durable families with
  checksum/reference remediation.
- `.aide/` generated/export/report material is control-plane evidence, not
  product truth.

## Test Boundary

Component-local tests live inside the component they validate, such as
`runtime/engine/tests`, `runtime/gateway/tests`, `runtime/connectors/tests`,
`surfaces/web/tests`, or `surfaces/native/tests`.

Root `tests/` is reserved for cross-component integration and end-to-end
coverage. Root `evals/` is reserved for system-level and replay-style
evaluation, not unit-style component checks.

`runtime/engine/interfaces/` is reserved for concrete dependency boundary paths
that other runtime components may rely on.
