# Repo Layout

Eureka's layout follows the component boundaries in [AGENTS.md](../AGENTS.md)
and the current architecture posture in [ARCHITECTURE.md](ARCHITECTURE.md).

```text
eureka/
  .aide/                  repo-local operating metadata and task packets
  .aide.local.example/    committed example for machine-local AIDE state
  .github/                repository automation
  control/                governance, audits, inventories, policies, evidence
  contracts/              schemas, contracts, packets, and public authority
  runtime/                Python reference runtime
  surfaces/               web, CLI, API, text, file, lite, and native projections
  site/                   static site source and generated static artifact tree
  snapshots/              snapshot schemas and public-safe examples
  docs/                   human documentation
  evals/                  repo-level evaluations
  examples/               public-safe fixtures, packs, and examples
  tests/                  cross-component and repo-operating tests
  tools/                  implementation helpers
  scripts/                stable command wrappers
  release/                release and hosting plans
  external/               pinned outside references
  archive/                retired, historical, or quarantined material
  native/                 native client project root and skeletons
  crates/                 Rust parity and future migration lane
```

## Ownership Intent

- `control/` owns governance and planning assets, not runtime behavior.
- `contracts/` owns shared meaning, packets, schemas, and public boundaries.
- `runtime/` owns Python reference runtime behavior.
- `surfaces/` owns user-facing projections.
- `site/` owns static site source and generated static publication artifacts.
- `snapshots/` owns read-only snapshot schema/examples.
- `tools/` owns substantive validator/generator/auditor implementations.
- `scripts/` owns stable command entry points that wrap `tools/`.
- `release/` owns release and hosting plans, not generated release output.
- `archive/` owns retained historical material that is not active authority.

## Generated And Local State

Do not commit local instances, private caches, raw logs, tokens, provider
credentials, raw live source responses, or full-discovery raw output. Full
discovery artifacts should live outside the repo, normally under
`../eureka-test-runs/<run-id>`.

`site/dist/` is the governed generated static artifact tree. It is not a Python
backend deployment and must not be treated as public launch evidence by itself.

## Test Boundary

Component-local tests live inside the component they validate. Root `tests/` is
for cross-component, hardening, operation, integration, and end-to-end checks.
Root `evals/` is for system-level and replay evaluations.

## References

- [Root README](../README.md)
- [Architecture](ARCHITECTURE.md)
- [Test and eval lanes](operations/TEST_AND_EVAL_LANES.md)
