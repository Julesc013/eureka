# Repository Layout Migration Plan

This plan was the safe follow-on to `REPO-LAYOUT-CANON-01`. Its active move
phases are superseded by `EUREKA-STRUCTURE-BIG-BANG-01`, which performed the
bounded reconciliation with a path migration map and validation evidence.

## Phase 0 - Canon Lock

Task: `REPO-LAYOUT-CANON-01`

Acceptance:

- Root allowlist contract exists.
- Root ownership contract exists.
- Naming contract exists.
- Generated artifact exception contract exists.
- Validator and focused tests exist.
- Known debt is recorded.
- No files are moved.
- No runtime behavior changes.

## Phase 1 - Inventory

Task: `REPO-LAYOUT-INVENTORY-02`

Status: superseded by `EUREKA-STRUCTURE-BIG-BANG-01`.

Acceptance:

- Tracked inventory is captured from `git ls-files`.
- Source, generated artifacts, retained evidence, archive material, fixtures,
  runtime projections, and local state are classified separately.
- Move candidates are mapped without moving files.
- `data/`, `deploy/`, `archive/prototypes/legacy_runtime`,
  `surfaces/web/workbench/local_html`, `contracts/schema/control`, and `scripts/` are all accounted
  for.

## Phase 2 - Generated Artifact Cleanup

Task: `REPO-LAYOUT-GENERATED-03`

Status: completed for top-level `data/`; generated public-index artifacts now
live under `site/dist/data/public_index`.

Acceptance:

- `site/dist`, `snapshots/examples/static_snapshot_v0`, and `site/dist/data/public_index`
  each have current generator and check policy.
- `site/dist/data/public_index` is moved, renamed, or reapproved with explicit artifact
  authority.
- Generated audit material remains excluded from active source authority.

## Phase 3 - Tools And Scripts Split

Task: `REPO-LAYOUT-TOOLS-04`

Status: completed for Python command files; `scripts/` now provides wrappers
over `tools/` implementations.

Acceptance:

- `scripts/` contains thin wrappers only.
- Substantive validators, auditors, builders, reporters, generators, migration
  tools, and release helpers are under `tools/`.
- Existing command entry points keep stable wrapper paths where needed.

## Phase 4 - Archive Classification

Task: `REPO-LAYOUT-ARCHIVE-05`

Status: completed for `control/prototypes/legacy_runtime`, now archived under
`archive/prototypes/legacy_runtime`.

Acceptance:

- Retired prototypes and historical material are moved or mapped to archive
  policy.
- Active scans exclude archive paths.
- Any retained archive material has a manifest or README when needed.

## Phase 5 - Contract Authority Cleanup

Task: `R0-03 / REPO-LAYOUT-CONTRACT-TAXONOMY-CLEANUP`

Status: completed for `control/schemas`, now under `contracts/schema/control`.

Acceptance:

- Product schemas and packets are authoritative under `contracts/`.
- `contracts/schema/control` is scoped to governance-only evidence with migration backlog.
- Examples and fixtures do not masquerade as canonical registry truth.
- Workbench view-model contract location is reserved under
  `contracts/view/pages/workbench/`.
- Search Interaction packet contract location is reserved under
  `contracts/search/interaction/`.
- No broad file moves or runtime behavior changes are performed in R0-03.

Follow-up task: `REPO-LAYOUT-CONTRACT-AUTHORITY-MIGRATION-01`, if migration is
needed after Workbench/Search contract locations are accepted.

## Phase 6 - Workbench Surface Ownership

Task: `REPO-LAYOUT-WORKBENCH-SURFACE-07`

Status: completed for `runtime/local_workbench`, now under
`surfaces/web/workbench/local_html`.

Acceptance:

- Workbench presentation authority is under `surfaces/web/workbench`.
- `surfaces/web/workbench/local_html` is retired, moved, or narrowed to runtime-only
  service proof material.
- Runtime exposes packets/services consumed by surfaces; it does not own HTML
  presentation.

## Proof Gates

Each phase should run the smallest fitting validation lane and report exact
results:

- `python scripts/validate_repo_structure_canon.py`
- `python scripts/check_architecture_boundaries.py` when runtime, gateway,
  connector, or surface boundaries are touched.
- `python scripts/check_generated_artifact_cleanliness.py --check --json` when
  generated artifacts are touched.
- Focused unit tests for the changed validators or contracts.
- AIDE Lite validation when AIDE operating metadata is touched.
