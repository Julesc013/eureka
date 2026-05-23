# Eureka Structure Compatibility Shim Audit v1

## Summary

This audit verifies the remaining old runtime taxonomy paths after the structure closeout. The inspected old paths are compatibility shims only: their active implementations live under canonical runtime families, and the old first-level packages are retained for import stability.

No runtime behavior, source connector behavior, public search behavior, live-source behavior, or production-readiness status was intentionally changed.

## Classification Result

- Old paths retained as compatibility shims: `19`
- Old paths removed: `0`
- Active duplicate implementation paths remaining: `0`
- Stale duplicate paths found: `0`

## Retained Shims

| Old path | Canonical path |
| --- | --- |
| `runtime/candidate_index` | `runtime/index/candidate` |
| `runtime/evidence_ledger` | `runtime/evidence/ledger` |
| `runtime/local_appliance` | `runtime/local/appliance` |
| `runtime/local_eval` | `runtime/local/eval` |
| `runtime/local_foundry` | `runtime/local/foundry` |
| `runtime/local_network` | `runtime/local/network` |
| `runtime/local_operator` | `runtime/local/operator` |
| `runtime/local_review` | `runtime/local/review` |
| `runtime/local_service` | `runtime/local/service` |
| `runtime/local_worker` | `runtime/local/worker` |
| `runtime/public_index` | `runtime/index/public` |
| `runtime/review_queue` | `runtime/review/queue` |
| `runtime/search_hunt` | `runtime/search/hunt` |
| `runtime/search_need` | `runtime/search/need` |
| `runtime/search_quality` | `runtime/search/quality` |
| `runtime/source_cache` | `runtime/source/cache` |
| `runtime/source_observation` | `runtime/source/observation` |
| `runtime/source_registry` | `runtime/source/registry` |
| `runtime/workunit_queue` | `runtime/worker/workunit_queue` |

Each retained shim now has a `README.md` marker. `control/policies/path_taxonomy_policy.json` requires every runtime compatibility path to contain only `__init__.py` and `README.md`.

## Removed Paths

None.

## Active Duplicate Paths

None found in the inspected old/new runtime pairs. The old paths remain import shims, not active implementation homes.

## Validator Updates

- `tools/validators/validate_path_taxonomy.py` now enforces required files for compatibility paths.
- `control/policies/path_taxonomy_policy.json` allows and requires `README.md` shim markers.
- `tests/tools/test_validate_path_taxonomy.py` covers missing marker and stray implementation-file failure cases.

## Validation

| Command | Status |
| --- | --- |
| `git diff --check` | pass; line-ending warnings only |
| `python scripts/validate_repo_structure_canon.py --json` | pass |
| `python scripts/validate_repo_structure_canon.py --strict --json` | pass |
| `python scripts/check_architecture_boundaries.py` | pass |
| `python scripts/validate_path_taxonomy.py --json` | pass; classified debt count remains `46` |
| `python scripts/validate_taxonomy_closeout_policy.py --json` | pass |
| `python -m unittest tests.tools.test_validate_path_taxonomy` | pass; `3` tests |
| `python -m unittest tests.tools.test_validate_path_taxonomy tests.tools.test_validate_taxonomy_closeout_policy tests.operations.test_repo_structure_canon` | pass; `11` tests |
| Runtime shim import smoke | pass; `38` canonical and compatibility modules imported |
| `py -3 .aide/scripts/aide_lite.py snapshot` | pass |
| `py -3 .aide/scripts/aide_lite.py index` | pass |
| `py -3 .aide/scripts/aide_lite.py context` | pass |
| `py -3 .aide/scripts/aide_lite.py validate` | pass |
| `py -3 .aide/scripts/aide_lite.py doctor` | pass |
| `python scripts/eureka_test_select.py --changed --failed-first --json` | pass selector; full discovery not required for changed-path mode |
| `python scripts/eureka_test_select.py --promotion --json` | pass selector; full discovery required only for explicit promotion gate |
| `python scripts/validate_test_lane_policy.py` | pass |
| `python -m unittest tests.operations.test_test_lane_policy` | pass; `1` test |
| `python -m unittest tests.scripts.test_eureka_test_select tests.scripts.test_validate_test_lane_policy` | pass; `5` tests |
| `python scripts/validate_public_static_site.py` | pass |
| `python scripts/validate_pack_set.py` | pass |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | pass; no generated drift, no network, no model provider use, no site/dist mutation |

Full unittest discovery was not rerun in this audit because no broad runtime imports or implementation files changed; the changed-path selector did not require it. The promotion selector continues to require full discovery for explicit promotion/release gates.

This audit does not claim full removal of all taxonomy debt; it only resolves the old/new runtime shim ambiguity.
