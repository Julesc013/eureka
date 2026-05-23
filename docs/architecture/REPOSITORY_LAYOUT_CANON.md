# Repository Layout Canon

This canon defines Eureka's active source ownership roots after the structure
reconciliation pass.
It is machine-readable first:

- `contracts/repo/root_allowlist.contract.toml`
- `contracts/repo/root_ownership.contract.toml`
- `contracts/repo/naming.contract.toml`
- `contracts/repo/generated_artifact_exceptions.contract.toml`

The validator is `scripts/validate_repo_structure_canon.py`.

## Verdict

The repository is bootstrap and pre-product. EUREKA-STRUCTURE-BIG-BANG-01 reconciled the recorded layout debt without claiming production readiness:
generated public-index artifacts now live under `site/dist/data/public_index`,
deployment definitions under `release/`, retired prototypes under `archive/`,
schema authority under `contracts/schema/control`, workbench presentation under
`surfaces/web/workbench/local_html`, and substantive tool implementations under
`tools/` behind `scripts/` wrappers.

## Canonical Roots

| Root | Ownership |
| --- | --- |
| `.aide/` | Repo-local AIDE Lite policy, adapters, prompts, and compact context support. |
| `.github/` | Repository automation and GitHub workflow definitions. |
| `control/` | Governance, inventories, audits, policies, task state, and planning evidence. |
| `contracts/` | Schemas, packets, view models, public contracts, and machine-readable product authority. |
| `runtime/` | Python reference backend, kernel behavior, runtime services, gateway, connectors, and stores. |
| `surfaces/` | Web, API, CLI, and TUI projection surfaces and adapters. |
| `native/` | Real native client projects, build metadata, platform matrix, and native shared libraries. |
| `crates/` | Rust parity and future production-lane experiments. |
| `site/` | Static site source and explicitly inventoried committed static artifact exceptions. |
| `snapshots/` | Snapshot schemas, deterministic seed examples, and offline interchange artifacts. |
| `examples/` | Fixtures, examples, demo corpora, and synthetic packs. |
| `docs/` | Human explanation of architecture, operations, references, and roadmap. |
| `tests/` | Verification. |
| `evals/` | Evaluation packets, query benchmarks, replay material, and eval scaffolding. |
| `tools/` | Substantive validators, auditors, builders, reporters, generators, and migration tools. |
| `scripts/` | Thin executable wrappers and command entry points. |
| `release/` | Deploy, package, promotion, and release definitions or recipes. |
| `external/` | Pinned outside references, specs, upstream snapshots, and license notes. |
| `archive/` | Retired, quarantined, superseded, generated, or historical material excluded from active scans. |

`tools/`, `release/`, and `archive/` are allowed even when absent.

## Native Rule

Do not absorb top-level `native/` into `surfaces/native/`.

`native/` is the canonical root for actual native client/project ownership:
native projects, platform matrices, build metadata, and native shared libraries.

`surfaces/native/`, if retained, may only own projection adapters, docs, or
examples. It must not supersede `native/` and must not become native project
authority.

## Boundary Rules

`control/` must not own executable product runtime.

`contracts/` owns product schemas and packets. It must not contain real content
payloads.

`runtime/` owns backend/kernel/runtime services. It must not own presentation
templates.

`surfaces/` owns product projections over runtime services and contracts. The
Workbench presentation target is `surfaces/web/workbench`.

`scripts/` remains allowed as the stable command-entry root. Long tool
implementations belong under `tools/`.

`examples/` contains examples and fixtures, not registry truth.

## Generated Artifact Policy

Committed generated or generated-like artifacts require a contract exception with
an owner, generator or governing command, check command, and no-manual-edit
policy. Current explicit exceptions include:

- `site/dist`
- `snapshots/examples/static_snapshot_v0`
- `site/dist/data/public_index`
- `control/audits/*/generated`
- `.aide/generated`
- `.aide/cache`
- `.aide/export`
- `.aide/reports`

`site/dist/data/public_index` is accepted only as committed generated public
artifact material under the static-site generated-artifact policy.

## Resolved Debt

Resolved layout debt is listed in `control/inventory/repo_layout_known_debt.json`
and the move map in
`control/audits/eureka-structure-big-bang-v1/path_migration_map.json`.

Product/public contract authority remains under `contracts/`;
`contracts/schema/control/` is retained as migrated schema authority and must
not be reintroduced under `control/`. `examples/` and `runtime/` are not
contract authority.

Future broad layout moves still require tracked inventory, a move map,
reference updates, and validation evidence.

## No Claims

This canon does not claim production readiness, public launch readiness, or
Workbench implementation progress.
