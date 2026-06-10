# Validation Report

Task: `SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-05`

Status: `PASS_WITH_WARNINGS`

## Ingest Validation

| Check | Result |
|---|---|
| status exists | PASS |
| summary exists | PASS |
| terminal summary | PASS |
| approved command | PASS |
| summary current to `HEAD` | PASS |
| failures represented | PASS; `39` |
| errors represented | PASS; `0` |
| skipped represented | PASS; `0` |
| failure families parseable | PASS; `24` raw families classified into `4` groups |
| failed tests inventory | PASS; `39` failed tests |
| raw logs copied into repo | no |

## Boundary Checks

| Boundary | Result |
|---|---|
| full discovery run inside AI | no |
| runtime behavior changed | no |
| product index mutated | no |
| reviewed artifact records created | no |
| verified artifact claims created | no |
| public alpha launched | no |
| `dev -> main` promoted | no |

## Local Validation

| Command | Result |
|---|---|
| `python scripts/check_git_task_state.py --mode start-task --task-id SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-05` | PASS with branch-name warning only |
| `python scripts/check_full_discovery.py --run-id source_snapshot_full_discovery_rerun_05 --json` | PASS command execution; terminal status `fail`, 5643 tests, 39 failures, 0 errors |
| `python -m json.tool docs/reference/validation/source_snapshot_full_discovery_ingest_05/FULL_DISCOVERY_SUMMARY_INDEX.json` | PASS |
| `python -m json.tool docs/reference/validation/source_snapshot_full_discovery_ingest_05/FAILURE_FAMILY_INDEX.json` | PASS |
| `git diff --check` | PASS |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS |
| `python scripts/check_architecture_boundaries.py` | PASS; 921 Python files checked |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | PASS; status `pass` |
| `py -3 scripts/eureka_test_select.py --changed --failed-first --json` | PASS; selected L0 static preflight only |

## Focused Tests

No focused subsystem tests were selected for this docs-only ingest. Full
discovery was not run inside the AI session; this package ingests the external
run result.
