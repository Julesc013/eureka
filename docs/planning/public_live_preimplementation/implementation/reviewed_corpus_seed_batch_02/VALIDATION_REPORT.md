# Validation Report

## Status

PASS_WITH_WARNINGS

## Required Commands

| Command | Result |
|---|---|
| `git diff --check` | PASS with Windows LF-to-CRLF checkout warning for `.aide/context/latest-task-packet.md` |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS |
| `python scripts/check_architecture_boundaries.py` | PASS, no architecture-boundary violations |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | PASS |
| `py -3 scripts/eureka_test_select.py --changed --failed-first --json` | PASS; selected L0 static preflight and L1 focused unit lanes |
| focused batch 02 tests | PASS, 24 tests |
| `python scripts/validate_test_lane_policy.py` | PASS |
| `python -m unittest tests.operations.test_test_lane_policy` | PASS, 1 test |
| `python -m unittest tests.scripts.test_eureka_test_select` | PASS, 3 tests |
| `python -m unittest tests.scripts.test_validate_test_lane_policy` | PASS, 2 tests |

## Full Discovery

Full unittest discovery was not run inside the AI session. Source/snapshot
closeout should create the external full-discovery handoff.

## Warnings

- Public alpha corpus gate remains `FAIL_INSUFFICIENT_REVIEWED_CORPUS`.
- External full discovery remains deferred to `SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01`.
- The Windows 98 driver query remains blocked pending user hardware details.
