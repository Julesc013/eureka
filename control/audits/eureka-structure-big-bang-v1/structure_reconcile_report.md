# Eureka Structure Big Bang v1

## Summary

EUREKA-STRUCTURE-BIG-BANG-01 reconciled the active repository layout with the repo canon in `contracts/repo/*`, `AGENTS.md`, and `docs/REPO_LAYOUT.md`.

The pass removed active top-level `data/` and `deploy/` roots, moved obsolete control/prototype authority out of `control/`, moved local HTML workbench presentation under `surfaces/web/`, and converted `scripts/` into compatibility wrappers over implementation files in `tools/`.

## Before And After Roots

Before active roots from the before-state report:

`.aide`, `.aide.local.example`, `.github`, `contracts`, `control`, `crates`, `data`, `deploy`, `docs`, `evals`, `examples`, `external`, `native`, `runtime`, `scripts`, `site`, `snapshots`, `surfaces`, `tests`

After active roots from strict repo-structure validation:

`.aide`, `.aide.local.example`, `.github`, `archive`, `contracts`, `control`, `crates`, `docs`, `evals`, `examples`, `external`, `native`, `release`, `runtime`, `scripts`, `site`, `snapshots`, `surfaces`, `tests`, `tools`

Changed top-level roots:

- Removed active tracked roots: `data`, `deploy`
- Added active tracked roots: `archive`, `release`, `tools`

## Moved Paths

Machine-readable move details are recorded in `control/audits/eureka-structure-big-bang-v1/path_migration_map.json`.

Move counts:

- Total migration-map entries: 801
- Root cleanup moves: 2
- Authority cleanup moves: 1
- Surface cleanup moves: 1
- Tooling cleanup moves: 795
- Archive moves: 1

Primary directory moves:

- `data/public_index` -> `site/dist/data/public_index`
- `deploy/render/render.yaml` -> `release/render/render.yaml`
- `deploy/README.md` -> `docs/operations/hosting/render_deployment.md`
- `control/schemas` -> `contracts/control_schemas`
- `control/prototypes/legacy_runtime` -> `archive/prototypes/legacy_runtime`
- `runtime/local_workbench` -> `surfaces/web/workbench/local_html`
- `scripts/*.py` implementations -> `tools/{validators,generators,auditors,reporters,migrations,release}/`

## Deleted Paths

Deleted tracked content: none.

Empty active directories `data/`, `deploy/`, and `control/prototypes/` were removed after their tracked content moved.

## Archived Paths

- `archive/prototypes/legacy_runtime` now holds the formerly active `control/prototypes/legacy_runtime` tree.

## Compatibility Wrappers

Compatibility wrappers created or updated: 795.

All tracked `scripts/*.py` files are thin wrappers marked with `EUREKA_SCRIPT_COMPAT_WRAPPER = True`. Wrappers preserve existing command entrypoints and import compatibility while implementation now lives under `tools/`.

## Validators Updated

Updated validators and policies include:

- Repo-structure canon validator and tests.
- Runtime architecture leakage policy and validator expectations for migrated control schemas and generated public-index artifacts.
- Public search/static-site validators for `site/dist/data/public_index`.
- Relay, native, product-contract, wrapper, and public-search rehearsal validators to follow wrapper targets where needed.
- Workbench and projection validators for `surfaces/web/workbench/local_html`.

## Docs Updated

Updated docs and inventories include:

- `docs/REPO_LAYOUT.md`
- `docs/architecture/REPOSITORY_LAYOUT_CANON.md`
- `docs/operations/hosting/render_deployment.md`
- `scripts/README.md`
- `tools/README.md` and tool-category README files
- `control/inventory/repo_layout_known_debt.json`
- `control/inventory/repo_layout_root_inventory.json`
- AIDE/repo metadata carrying path references

## Tests Run

Passed:

- `git diff --check`
- `python scripts/validate_repo_structure_canon.py --json`
- `python scripts/validate_repo_structure_canon.py --strict --json`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `python scripts/eureka_test_select.py --promotion --json`
- `python scripts/build_public_search_index.py --check --json`
- `python scripts/validate_public_search_index.py --json`
- `python scripts/validate_static_site_search_integration.py --json`
- `python site/build.py --check`
- `python scripts/validate_public_static_site.py`
- `python site/validate.py`
- `python scripts/validate_pack_set.py --all-examples --json`
- `python scripts/validate_public_search_index_builder.py`
- `python scripts/validate_contract_taxonomy.py`
- `python scripts/audit_runtime_architecture_leakage.py --check --json`
- `python scripts/validate_runtime_architecture_leakage.py`
- `python scripts/validate_workbench_result_lanes.py`
- `python scripts/validate_workbench_foundation.py`
- `python scripts/validate_test_lane_policy.py`
- `python -m unittest discover -s tests/connectors -t .`
- Focused unittest slices for repo canon, architecture boundaries, runtime leakage, workbench, static site, pack contracts, wrapper behavior, native summaries, archived prototype imports, relay planning, and public-search rehearsal.

Supplemental broad discovery:

- `python -m unittest discover -s tests -t .` was run before the final remediation pass and failed with path fallout plus dirty-tree/generated-artifact assertions. The structure-caused failures identified there were remediated and rerun through focused connector, operation-audit, wrapper, native, relay, and public-search rehearsal slices.

## Failures Remediated

- Public index path failures after moving `data/public_index` were fixed by updating builders, validators, runtime public search loading, and generated static-site summaries.
- `site/build.py --clean` deleting the canonical public index was fixed by preserving/restoring `site/dist/data/public_index` during clean builds.
- Runtime architecture leakage failures for migrated `contracts/control_schemas` and generated public-index artifacts were fixed in the policy classification.
- Archived prototype import failures were fixed by updating tests, tools, and archived prototype modules to `archive.prototypes.legacy_runtime`.
- Script wrapper import/inspection failures were fixed by strengthening wrapper import behavior and preserving legacy inspection markers where tests still inspect the script file.
- Native summary validation was fixed after moving implementation to `tools/reporters`.
- Relay and public-search validators were updated to understand wrapper-backed scripts.

## Known Remaining Debt

No repo-structure validator debt remains.

The repository remains bootstrap and pre-product. Historical audit documents may still mention old paths as before-state or resolved-debt evidence.

## Explicit Non-Claims

- This does not claim production readiness.
- This does not claim public launch readiness.
- This does not intentionally change runtime behavior.
- This does not intentionally change source connector behavior.
- This does not intentionally change public search behavior.
- No generated output is treated as source truth.
- No path is treated as object identity.
