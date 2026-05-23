# Contract Taxonomy

R0-03 defines where contract and schema authority lives before Workbench
Foundation. It does not move files, delete schemas, or change runtime behavior.

## Authority Classes

`PRODUCT_PUBLIC_CONTRACT`

Public API packets, source-family contracts, view models, snapshot formats, pack
formats, and interchange records that future surfaces may consume.

`PRODUCT_INTERNAL_CONTRACT`

Stable runtime, store, or boundary packets shared between product components.
These are internal to Eureka but still governed contract law.

`CONTROL_SCHEMA`

Governance, audit, inventory, task, report, validator, preview, fixture, or
deprecated schema records used by the control plane.

`POLICY_DOCUMENT`

Policy records, source access policies, safety gates, task gates, and non-claim
documents. Policies govern work but do not become product payload schemas.

`INVENTORY_RECORD`

Observed repository or project state, current task state, debt records, and
validation results. Inventory records describe state; they do not override
machine-readable contracts.

`AUDIT_SCHEMA_OR_REPORT`

Audit reports, audit schemas, and generated audit summaries. They preserve
evidence and provenance, not product runtime truth.

`FIXTURE_SCHEMA`

Schemas used only for examples, tests, fixture replay, and synthetic proof
payloads.

`EXAMPLE_PAYLOAD`

Example records, fixture outputs, demo corpora, and synthetic packs. Examples
are never canonical registry truth.

`GENERATED_ARTIFACT`

Generated or generated-like output that needs generator, check, and no-manual-edit
policy.

`DEPRECATED_OR_QUARANTINE`

Legacy, prototype, superseded, or migration-candidate material retained for
traceability.

## Root Ownership

`contracts/` owns `PRODUCT_PUBLIC_CONTRACT` and `PRODUCT_INTERNAL_CONTRACT`.
Future Workbench view-model contracts are reserved under
`contracts/view/pages/workbench/`. Future Search Interaction packets are reserved
under `contracts/search/interaction/`.

`contracts/testing/` owns `PRODUCT_INTERNAL_CONTRACT` records for
machine-readable test-lane, test-selection, and test-result packet schemas such
as `contracts/testing/test_selection_result.v0.json`. These contracts may be
consumed by scripts, validators, tests, AIDE, and future CI tooling. They must
not become runtime implementation, product data, example payload authority,
generated artifact output, or test result storage.

`contracts/schema/control/` may own `CONTROL_SCHEMA` only. Product contracts are not
allowed under `contracts/schema/control/`. Current control schemas are retained for audit,
fixture, preview, policy, validator, task, and deprecated records, with migration
backlog recorded in `control/inventory/contract_taxonomy_migration_backlog.json`.

`control/policies/` owns `POLICY_DOCUMENT` records.

`control/inventory/` owns `INVENTORY_RECORD` records.

`control/audits/` owns `AUDIT_SCHEMA_OR_REPORT` evidence and generated audit
outputs.

`examples/` owns `FIXTURE_SCHEMA` and `EXAMPLE_PAYLOAD` only. It must not be
used as registry truth.

`runtime/` owns implementation and implementation-local validation helpers only.
It must not become contract authority.

`scripts/` and future `tools/` own validators, auditors, generators, and wrappers.
They do not own schema semantics.

## Duplicate Authority Risks

R0-03 records current risks rather than hiding them:

- `contracts/schema/control/policies/packs/**` vs `contracts/pack/**`
- `contracts/source/registry/**` vs `contracts/source/records/**`
- `contracts/source/cache/**` vs `contracts/stores/source_cache_*.json`
- `contracts/runtime/**` vs runtime implementation-local helpers
- `contracts/archive/**` vs the top-level `archive/` historical root
- `control/inventory/repo_layout_*.json` vs `contracts/repo/*.contract.toml`

Contracts win over docs and inventory when they disagree. Inventory and audit
files may explain or report state, but they do not become the source of truth.

## Workbench And Search Interaction

Workbench Foundation should put route/view-model contract law under
`contracts/view/pages/workbench/`; `surfaces/web/workbench/` owns presentation and
`surfaces/web/workbench/local_html/` is the migrated local HTML renderer.

Search Interaction should put query, compiled intent, resolution run, result
lane, control command, feedback, absence, coverage, and discovery trail packets
under `contracts/search/interaction/`.

## No Claims

This taxonomy does not claim production readiness, public launch readiness, full
Archive.org integration, extraction readiness, model/provider use, or marketplace
readiness.
