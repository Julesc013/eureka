# Validation Report

## Status

`PASS_WITH_WARNINGS`

## Focused Labels

The exact architecture-boundary labels were rerun after repair through an external compact log because this lane takes more than 120 seconds:

```text
python -m unittest \
  tests.operations.test_legacy_runtime_leakage_remediation.LegacyRuntimeLeakageRemediationTests.test_validator_passes_current_repo \
  tests.operations.test_runtime_architecture_leakage.RuntimeArchitectureLeakageTests.test_validator_passes_current_repo_or_reports_only_known_allowlisted \
  tests.scripts.test_validate_repo_structure_canon.RepoStructureCanonValidatorScriptTest.test_validator_json_records_canon_and_resolved_debt \
  tests.scripts.test_validate_repo_structure_canon.RepoStructureCanonValidatorScriptTest.test_validator_strict_passes_after_reconcile
```

Result:

```text
PASS, 4 tests, 233.713 seconds
```

Compact summary:

```text
D:\Projects\Eureka\eureka-test-runs\architecture_boundary_drift_repair_01\focused_architecture_boundary_labels_summary.json
```

## Direct Validators

| Command | Result |
|---|---|
| `python scripts/validate_runtime_architecture_leakage.py --json` | PASS |
| `python scripts/validate_legacy_runtime_leakage_remediation.py --json` | PASS |
| `python scripts/validate_repo_structure_canon.py --json` | PASS |
| `python scripts/validate_repo_structure_canon.py --strict --json` | PASS |

## Final Validation

| Command | Result |
|---|---|
| `git status --short` | PASS, task-scoped changes only |
| `git diff --check` | PASS, line-ending notices only |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS |
| `python scripts/check_architecture_boundaries.py` | PASS |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | PASS |
| `python -m json.tool control/policies/runtime_architecture_leakage_allowlist.json > $null` | PASS |
| `py -3 scripts/eureka_test_select.py --changed --failed-first --json` | PASS, selected L0/L1 lanes |
| `python scripts/validate_test_lane_policy.py` | PASS |
| `python -m unittest tests.operations.test_test_lane_policy` | PASS |
| `python -m unittest tests.operations.test_test_impact_map` | PASS |
| `python -m unittest tests.operations.test_test_failure_ledger` | PASS |
| `python -m unittest tests.scripts.test_eureka_test_select` | PASS |
| `python -m unittest tests.scripts.test_validate_test_lane_policy` | PASS |

## Generated Artifact Handling

`control/audits/r0-remediation-legacy-leakage-01-v0/remediation_report.json` was intentionally left unchanged after validation showed it is treated as generated audit evidence. Current counts are carried by `control/inventory/legacy_runtime_leakage_remediation_result.json` and `control/inventory/legacy_runtime_leakage_remaining_allowlist.json`; the legacy validator now permits the historical generated report to remain immutable while still requiring the current inventory count to match the fresh leakage audit.

## Full Discovery

Full unittest discovery was not run inside the AI session. The current external discovery already identified the repaired labels; a new external full-discovery run remains a later validation gate after the remaining failure families are repaired.

## Residual Warnings

- Public alpha remains blocked.
- Dev to main promotion remains blocked.
- `scripts_large_tool_tree` remains known repo-structure debt.
- The runtime architecture leakage allowlist now contains 2035 known allowlisted findings; newly added entries are exact, context-bound, and expire after `QUEUE-HANDOFF-DRIFT-REPAIR-01`.
