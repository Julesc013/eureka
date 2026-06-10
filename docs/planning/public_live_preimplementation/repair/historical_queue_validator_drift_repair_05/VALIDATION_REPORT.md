# Validation Report

## Focused Compile

```text
python -m py_compile tools\generators\hunt_queue_progress.py tools\generators\local_queue_progress.py scripts\validate_public_alpha_launch_defer.py scripts\validate_dev_to_main_promotion_03.py scripts\validate_dev_to_main_promotion_04.py
```

Result: `PASS`

## Focused Failure Labels

Representative rerun 05 failures:

```text
python -m unittest tests.operations.test_search_hunt_scripts tests.operations.test_local_instance_bootstrap tests.operations.test_public_alpha_launch_defer tests.operations.test_dev_to_main_promotion_03
```

Result: `PASS`

```text
tests_run: 24
failures: 0
errors: 0
```

Promotion and public-alpha defer group:

```text
python -m unittest tests.operations.test_public_alpha_launch_defer tests.operations.test_dev_to_main_promotion_03 tests.operations.test_dev_to_main_promotion_04 tests.scripts.test_validate_dev_to_main_promotion_03 tests.scripts.test_validate_dev_to_main_promotion_04
```

Result: `PASS`

```text
tests_run: 15
failures: 0
errors: 0
```

HUNT and LOCAL failure labels were rerun in smaller slices because the aggregate focused command exceeded the command timeout. All completed slices passed.

Slow LOCAL slices run sequentially:

```text
python -m unittest tests.operations.test_local_auto_test_scripts
python -m unittest tests.operations.test_local_http_service_scripts
python -m unittest tests.operations.test_local_lan_policy_scripts
python -m unittest tests.operations.test_local_lan_smoke_scripts
python -m unittest tests.operations.test_local_review_rebuild_smoke
python -m unittest tests.operations.test_local_runtime_composition_scripts
python -m unittest tests.operations.test_local_workbench_page_hardening_scripts
python -m unittest tests.operations.test_local_workbench_scripts
python -m unittest tests.operations.test_local_worker_scripts
```

Result: `PASS`

## Timeout Notes

The following aggregate commands timed out before producing a useful result and are not counted as validation passes:

```text
python -m unittest <all 39 rerun-05 failed-label modules>
python -m unittest <HUNT failed-label module bundle>
python -m unittest <LOCAL script bundle>
```

The timed-out bundles were replaced with smaller module slices.

## Changed-File Selector

```text
py -3 scripts\eureka_test_select.py --changed --failed-first --json
```

Result: `PASS`

Selected lanes:

```text
L0_static_preflight
L1_focused_unit
L2_impact_integration
```

Selected commands:

```text
git diff --check
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
python -m unittest tests.scripts.test_validate_test_lane_policy
python scripts/validate_test_lane_policy.py
python -m unittest tests.operations.test_test_lane_policy
python -m unittest tests.scripts.test_eureka_test_select
```

All selected commands passed.

## Standard Validation

```text
git diff --check
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
python scripts/check_full_discovery.py --run-id source_snapshot_full_discovery_rerun_05 --json
```

Result: `PASS`

`git diff --check` emitted Windows line-ending normalization notices for modified text files, not whitespace errors.

The rerun 05 full discovery check reported terminal `fail` as expected for the input failure:

```text
tests_run: 5643
failures: 39
errors: 0
```

## Gate State

The previous external full-discovery run is stale after this repair commit.

```text
source/snapshot release gate: blocked pending external rerun 06
public alpha gate: blocked
dev -> main promotion gate: blocked
```
