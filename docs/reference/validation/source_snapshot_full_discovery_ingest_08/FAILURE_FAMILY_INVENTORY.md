# Failure Family Inventory

## Result

Rerun 08 reported 12 raw unittest failure families and 23 failed tests.

The failures are validator expectation drift around historical queue and
promotion task assertions. The compact evidence does not indicate IA metadata
provider, SurfaceKernel, baseline renderer, or runtime behavior failure.

## Classified Families

### historical_queue_validator_drift

```text
test_count: 17
error_count: 0
risk: medium
recommended_next_repair_task: HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08
```

Representative labels:

- `tests.operations.test_search_hunt_track`
- `tests.operations.test_search_hunt_scripts`
- `tests.operations.test_search_hunt_ui_scripts`
- `tests.operations.test_search_hunt_command_scripts`
- `tests.operations.test_search_hunt_exhaustion_scripts`
- `tests.operations.test_search_need_scripts`
- `tests.operations.test_need_to_workunit_scripts`
- `tests.operations.test_background_hunt_runner_scripts`
- `tests.operations.test_hunt_remediation`
- `tests.operations.test_hunt_remediation_continue`
- `tests.operations.test_hunt_replay_scripts`
- `tests.operations.test_agent_research_scripts`
- `tests.operations.test_ai_escalation_scripts`
- `tests.operations.test_search_hunt_closeout`

Representative message:

```text
queue index/latest task packet must point to a historical HUNT successor or mark a historical HUNT task completed
```

Likely root cause:

```text
Historical HUNT validators still assert older successor/current-task allowlists after the queue advanced to IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00.
```

### historical_dev_to_main_promotion_validator_drift

```text
test_count: 4
error_count: 0
risk: medium
recommended_next_repair_task: HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08
```

Representative labels:

- `tests.operations.test_dev_to_main_promotion_03`
- `tests.operations.test_dev_to_main_promotion_04`
- `tests.scripts.test_validate_dev_to_main_promotion_03`
- `tests.scripts.test_validate_dev_to_main_promotion_04`

Representative message:

```text
post-promotion origin/main and origin/dev must match: 0 89
```

Likely root cause:

```text
Historical dev-to-main promotion validators still run against current branch divergence and old promotion assumptions even though dev-to-main promotion is blocked.
```

### public_alpha_defer_queue_validator_drift

```text
test_count: 2
error_count: 0
risk: medium
recommended_next_repair_task: HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08
```

Representative labels:

- `tests.operations.test_public_alpha_launch_defer`

Representative message:

```text
queue current recommended task must be active discovery or a later blocked repair/readiness task
```

Likely root cause:

```text
The public-alpha defer validator allowlist has not been updated for the IA metadata provider smoke queue successor.
```

## Repair Decision

No same-turn repair was applied.

Reason:

```text
The failure spans multiple historical validator surfaces and 12 raw unittest failure families. Repairing it safely requires a dedicated validator-drift repair task rather than a narrow single-family patch in this ingest turn.
```

