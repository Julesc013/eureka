# Eureka Structure Second Pass Reconcile Report

## Summary

This pass reconciled the remaining high-confidence second-level structure debt after
the root cleanup commit `fae6b8814d193a3b8694de98954c8ec2dbab2415`.

The pass intentionally kept runtime behavior, source connector behavior, and public
search behavior unchanged. It made only low-risk path moves, wrapper additions,
validator updates, documentation updates, and explicit debt classification where a
broader move would touch active runtime or contract identity.

## Before And After Top-Level Roots

Before this pass, tracked top-level roots were:

`.aide/`, `.aide.local.example/`, `.github/`, `archive/`, `contracts/`,
`control/`, `crates/`, `docs/`, `evals/`, `examples/`, `external/`,
`native/`, `release/`, `runtime/`, `scripts/`, `site/`, `snapshots/`,
`surfaces/`, `tests/`, `tools/`.

After this pass, tracked top-level roots are unchanged. The root-level cleanup from
the prior pass remains intact: no active top-level `data/` or `deploy/` root is
present.

Focused generated-path inspection found:

- `site/dist/` has 58 tracked public static artifact files.
- `tmp/` has no tracked files and is ignored.
- Tracked `/dist/` paths are limited to `site/dist/` and native distribution
  README placeholders.

## Moved Paths

Logical path moves:

- `release/render/render.yaml` -> `release/hosting/render/render.yaml`
  to classify the Render template as hosting release material.
- `surfaces/native/cli/` -> `surfaces/cli/`
  to represent CLI as a first-class surface family rather than a native subroot.

Git detected 36 file-level renames at a 20 percent similarity threshold, including
the Render template and the CLI package, formatters, and tests.

The machine-readable migration map is
`control/audits/eureka-structure-second-pass-v1/path_migration_map.json`.

## Deleted Paths

No tracked content was deleted as content. The old move sources are absent only
because their content was moved to equivalent new paths.

## Archived Paths

No new path was archived in this pass. The archive guard was added so previously
archived Python under `archive/` is explicitly kept out of active imports.

## Compatibility Wrappers Created

Two `scripts/` compatibility wrappers were added:

- `scripts/validate_archive_import_guard.py`
- `scripts/validate_path_taxonomy.py`

The existing wrapper split remains intact; `scripts/` still acts as the command
entrypoint layer over `tools/`.

## Validators Updated

Updated or added validators:

- `tools/validators/check_architecture_boundaries.py`
  now treats each `surfaces/<family>/` package as its own surface namespace.
- `tools/validators/validate_native_client_contract.py`
  now recognizes `surfaces/cli/` as the CLI root.
- `tools/release/validate_hosted_public_search_wrapper.py`
  now points at `release/hosting/render/render.yaml`.
- `tools/validators/validate_repo_structure_canon.py`
  includes tracked AIDE generated/report exceptions.
- `tools/validators/validate_path_taxonomy.py`
  records second-level taxonomy debt without failing active validation.
- `tools/validators/validate_archive_import_guard.py`
  prevents active code from importing archived Python.
- `tools/auditors/audit_contract_taxonomy.py`
  deduplicates overlapping contract roots by repo-relative path.

## Docs Updated

Updated documentation and inventory references include:

- `docs/REPO_LAYOUT.md`
- `docs/BOOTSTRAP_STATUS.md`
- `docs/DECISIONS.md`
- `docs/ROADMAP.md`
- `docs/architecture/COMPATIBILITY_SURFACES.md`
- `docs/operations/PUBLIC_SEARCH_HOSTING.md`
- `docs/operations/TEST_AND_EVAL_LANES.md`
- `docs/operations/hosting/render_deployment.md`
- `docs/reference/NATIVE_CLIENT_CONTRACT.md`
- `surfaces/README.md`
- `surfaces/native/README.md`
- `surfaces/api/README.md`
- `surfaces/files/README.md`
- `surfaces/lite/README.md`
- `surfaces/text/README.md`
- `archive/README.md`
- `tests/README.md`
- affected `control/inventory/` and `control/audits/` path references.

## Tests Run

Pre-commit validation run:

- PASS: `git diff --check`
- PASS: `python scripts/validate_repo_structure_canon.py --json`
- PASS: `python scripts/validate_repo_structure_canon.py --strict --json`
- PASS: `python scripts/check_architecture_boundaries.py`
- PASS: `python scripts/eureka_test_select.py --changed --failed-first --json`
- PASS: `python scripts/eureka_test_select.py --promotion --json`
- PASS: `python scripts/validate_public_static_site.py`
- PASS: `python scripts/validate_pack_set.py --all-examples --json`
- PASS: `python site/build.py --check`
- PASS: `python scripts/build_public_search_index.py --check --json`
- PASS: `python scripts/validate_public_search_index.py --json`
- PASS: `python site/validate.py`
- PASS: `python scripts/validate_static_site_search_integration.py --json`
- PASS: `python scripts/validate_path_taxonomy.py --json`
- PASS: `python scripts/validate_archive_import_guard.py --json`
- PASS: `python scripts/validate_native_client_contract.py --json`
- PASS: `python scripts/validate_hosted_public_search_wrapper.py --json`
- PASS: `python -m unittest tests.tools.test_validate_archive_import_guard tests.tools.test_validate_path_taxonomy`
- PASS: `python -m unittest tests.architecture.test_check_architecture_boundaries`
- PASS: `python -m unittest discover -s surfaces/cli/tests -t .`
- PASS: focused integration slices covering acquisition, action plans,
  compatibility, decomposition, handoff, member access, real source coverage,
  and representations.
- PASS: selected focused operations/tooling tests for contract taxonomy,
  repo structure canon, workbench foundation, test lane policy, and hosted public
  search wrapper.

Pre-commit dirty-tree-sensitive discovery:

- FAIL as expected while staged changes existed:
  `python -m unittest discover -s tests -t . -f`
- Exact failure:
  `tests.operations.test_hunt_main_post_promotion_state.HuntMainPostPromotionStateTests.test_next_decision_requires_syn_and_main_promoted`
- Reason:
  `scripts.audit_hunt_main_promotion.build_promotion_records()` correctly
  reported `working_tree_clean_before: false`, returned the blocked promotion
  decision, and the test expects the clean-tree committed promotion decision.
- Remediation:
  Do not weaken the promotion gate. Rerun after committing, when the tree is
  clean.

Pre-commit generated artifact cleanliness:

- FAIL while staged audit evidence existed:
  `python scripts/check_generated_artifact_cleanliness.py --check --json`
- Reason:
  the validator intentionally treats uncommitted `control/audits/**` changes as
  generated/audit drift.
- Remediation:
  rerun after committing, when audit evidence is tracked and the tree is clean.

## Failures Remediated

- `tests.operations.test_contract_taxonomy_plan.ContractTaxonomyPlanTests.test_audit_script_runs_in_check_mode`
  failed because the contract taxonomy auditor counted overlapping contract
  roots twice after `contracts/control_schemas/` was present. The auditor now
  deduplicates by repo-relative path and the focused test passes.
- `tests.operations.test_hosted_public_search_wrapper` failed because the test
  still read `deploy/render/render.yaml`. It now reads
  `release/hosting/render/render.yaml` and the focused test passes.

## Known Remaining Debt

The path taxonomy validator records 133 known debt paths without failing active
validation. These are intentionally visible rather than silently accepted:

- `contracts/` still has fragmented families including `control_schemas`,
  `evidence_ledger`, `source_*`, `views`, `view_models`, `ui`, `projections`,
  `pages`, `search_interaction`, and `search_quality`.
- `runtime/` still has flat subsystem families including `local_*`, `source_*`,
  `candidate_index`, `public_index`, `evidence_ledger`, `review_queue`,
  `workunit_queue`, `resolution_run`, and search/query families.
- `examples/` still has many first-level historical task and fixture families.
- `.aide/` and `control/audits/**/generated/` remain large but now have explicit
  generated-retention policy coverage and repo-structure exceptions where needed.

These debts were not mass-moved in this pass because doing so safely would require
broader runtime, contract, validator, and fixture identity changes. The validator
now provides a governed map for future incremental moves.

## Explicit Non-Claims

- This pass did not intentionally change product behavior.
- This pass did not intentionally change source connector behavior.
- This pass did not intentionally change public search behavior.
- This pass does not claim production readiness or public launch readiness.
- This pass does not treat generated output as source truth.
- This pass does not treat paths as object identity.
- Passing taxonomy validation means known debt is classified, not eliminated.
