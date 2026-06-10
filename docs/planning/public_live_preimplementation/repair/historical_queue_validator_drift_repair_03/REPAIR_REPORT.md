# Repair Report

## Status

`PASS_WITH_EXTERNAL_RERUN_REQUIRED`

## Input

External full discovery rerun 03 was terminal and current to commit `2549af51`.

```text
tests_run: 5620
failures: 22
errors: 0
family: historical_queue_validator_drift
```

## Repair

Updated historical validator successor checks so completed HUNT, LOCAL, and dev-to-main promotion validation tasks accept the current later governance chain.

This is a validator repair only:

```text
runtime changed: no
contracts changed: no
surface behavior changed: no
queue rewound: no
public alpha launched: no
dev -> main promoted: no
```

## Files

```text
tools/generators/hunt_queue_progress.py
tools/generators/local_queue_progress.py
tools/validators/validate_local_appliance_track.py
scripts/validate_dev_to_main_promotion_03.py
scripts/validate_dev_to_main_promotion_04.py
tests/operations/test_hunt_main_promotion_gates.py
tests/operations/test_local_appliance_track.py
.aide/queue/index.yaml
```

## Rationale

The failed validators were historical completion checks. Their artifacts were still valid, but their queue-successor allowlists stopped at earlier source/snapshot and discovery tasks.

The current repo authority says the active chain has advanced through artifact evidence gates and full-discovery ingest 03. Rewinding the queue to old tasks would be false. The repair therefore expands successor recognition to the current and future numbered validation/artifact successors.

