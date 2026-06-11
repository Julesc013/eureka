# Validation Report

## External Validation

```text
python scripts/check_full_discovery.py --run-id source_snapshot_full_discovery_rerun_06 --json
```

Result:

```text
status: pass
tests_run: 5645
failures: 0
errors: 0
elapsed_seconds: 2774.221
```

## Ingest Validation

This ingest package records compact external evidence only.

```text
python -m json.tool docs\reference\validation\source_snapshot_full_discovery_ingest_06\FULL_DISCOVERY_SUMMARY_INDEX.json
python -m json.tool docs\reference\validation\source_snapshot_full_discovery_ingest_06\FAILURE_FAMILY_INDEX.json
git diff --check
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
py -3 scripts/eureka_test_select.py --changed --failed-first --json
python scripts/check_full_discovery.py --run-id source_snapshot_full_discovery_rerun_06 --json
```

Result: `PASS`

Selector result:

```text
selected_lanes: L0_static_preflight
focused tests selected: none
full discovery inside AI: not selected
```

## Gate State

```text
source/snapshot release gate: green_current
public alpha gate: blocked
dev -> main promotion gate: blocked
reviewed artifact gate: blocked_4_of_25
verified artifact gate: blocked_0
external artifact evidence gate: waiting_for_external_artifact_evidence
hardware details gate: waiting_for_user_hardware_details
```
