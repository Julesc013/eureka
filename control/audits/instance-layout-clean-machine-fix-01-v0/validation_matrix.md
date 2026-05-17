# Validation Matrix

- `python scripts/eureka_resolve_paths.py --json`: pass
- `python scripts/eureka_list_instances.py --json`: pass
- `python scripts/eureka_migrate_instance_layout.py --from ../eureka-instance --to ../instances/default --dry-run --json`: pass with warnings for absent legacy source and existing target
- `python scripts/validate_instance_layout_policy.py`: pass
- `python -m unittest tests.runtime.test_local_appliance_paths`: pass
- `python -m unittest tests.operations.test_clean_machine_bootstrap.CleanMachineBootstrapScriptTests.test_bootstrap_creates_temp_checkout_and_validates_instance`: pass
- `python -m unittest tests.operations.test_clean_machine_smoke.CleanMachineSmokeScriptTests.test_validator_passes_with_known_warning`: pass
- `python scripts/validate_clean_machine_bootstrap.py --json`: pass
- targeted broad subset: fail with 10 unrelated legacy/broad-lane failures and no instance-layout-caused failures remaining
- full unittest discovery: fail with 11 failures before final cleanup; 10 are the classified broad-lane failures, and 1 runtime vocabulary issue was repaired
- `python -m unittest tests.runtime.test_local_appliance_validation.LocalApplianceValidationTests.test_runtime_package_has_no_task_or_h_series_vocabulary`: pass after cleanup

`python scripts/validate_local_instance_bootstrap.py` still fails on a historical latest-task packet expectation for LOCAL-02. That is broad-lane validation debt and not part of the clean-machine path repair.
