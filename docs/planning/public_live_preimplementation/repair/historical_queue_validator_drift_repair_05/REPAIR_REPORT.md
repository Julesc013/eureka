# Repair Report

## Status

`PASS_WITH_EXTERNAL_RERUN_REQUIRED`

## Input

External full discovery rerun 05 was terminal and current when ingested.

```text
run_id: source_snapshot_full_discovery_rerun_05
tests_run: 5643
failures: 39
errors: 0
family: historical_queue_validator_drift
```

## Repair

Updated historical validator successor checks so completed HUNT, LOCAL, public-alpha defer, and dev-to-main promotion validation tasks accept the current later governance wait states.

Accepted wait states added where relevant:

```text
WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE
WAITING_FOR_EXTERNAL_FULL_DISCOVERY
WAITING_FOR_USER_HARDWARE_DETAILS
```

This is a validator repair only:

```text
runtime changed: no
contracts changed: no
surface behavior changed: no
queue rewound: no
public alpha launched: no
dev -> main promoted: no
artifact evidence invented: no
```

## Files

```text
tools/generators/hunt_queue_progress.py
tools/generators/local_queue_progress.py
scripts/validate_public_alpha_launch_defer.py
scripts/validate_dev_to_main_promotion_03.py
scripts/validate_dev_to_main_promotion_04.py
tests/operations/test_hunt_main_promotion_gates.py
tests/operations/test_local_appliance_track.py
```

## Rationale

The failed validators were historical completion checks. Their artifacts were still valid, but their queue-successor allowlists stopped before the current external evidence and hardware-detail waiting posture.

The current repo authority says the active chain has advanced past those historical HUNT, LOCAL, public-alpha, and promotion tasks. Rewinding the queue to old tasks would be false. The repair therefore expands successor recognition to current governed wait states without changing product behavior.

