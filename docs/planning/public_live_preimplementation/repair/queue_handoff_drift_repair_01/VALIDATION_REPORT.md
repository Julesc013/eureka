# Validation Report

## Status

`PASS_WITH_WARNINGS`

## Focused Queue-Handoff Labels

The 39-label combined queue-handoff lane was started and then stopped after
1045 seconds because it was too large for a focused AI-session lane. It wrote
compact evidence to:

```text
D:\Projects\Eureka\eureka-test-runs\queue_handoff_drift_repair_01\focused_queue_handoff_labels_summary.json
```

The labels were then validated in split lanes:

| Lane | Result |
|---|---|
| HUNT/post-HUNT labels | PASS, 15 tests |
| Public launch defer and promotion labels | PASS, 6 queue-specific tests |
| LOCAL bootstrap/appliance labels | PASS, 5 tests |
| LOCAL runtime/http/workbench/workunit/review labels | PASS, 5 tests |
| Clean machine/local auto/LAN/workbench hardening labels | PASS, 5 tests |
| Agent research and AI escalation labels | PASS, 2 tests |

One label from the original family remains failing, but its validator output is
contract/schema drift:

```text
tests.scripts.test_validate_temporal_semantic_interface_system.ValidateTemporalSemanticInterfaceSystemTest.test_validator_passes
```

## Direct Validators

| Command | Result |
|---|---|
| `python scripts/check_full_discovery.py --run-id source_snapshot_baseline_closeout_01 --json` | PASS command, external run remains fail |
| `python scripts/validate_temporal_semantic_interface_system.py --json` | FAIL, reclassified residual `contract_schema_drift` |
| `python scripts/validate_public_alpha_launch_defer.py --json` | PASS |
| `python scripts/validate_dev_to_main_promotion_03.py --json` | PASS |
| `python scripts/validate_dev_to_main_promotion_04.py --json` | PASS |

## Final Validation

| Command | Result |
|---|---|
| `git diff --check` | PASS, line-ending notices only |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS |
| `python scripts/check_architecture_boundaries.py` | PASS |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | PASS |
| `py -3 scripts/eureka_test_select.py --changed --failed-first --json` | PASS, selected L0/L1/L2 lanes |
| `python -m unittest tests.scripts.test_validate_test_lane_policy` | PASS |
| `python scripts/validate_test_lane_policy.py` | PASS |

## Full Discovery

Full discovery was not rerun inside the AI session. External run
`source_snapshot_baseline_closeout_01` remains the current red full-discovery
evidence until the residual repair families are fixed and a new external rerun
is requested.

## Final Recommendation

`PASS_WITH_WARNINGS`: queue-specific handoff drift is repaired, while residual
`source_snapshot_baseline_drift`, `generated_artifact_drift`, and
`contract_schema_drift` remain blocking for public alpha, source/snapshot
release readiness, and `dev -> main` promotion.
