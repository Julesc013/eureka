# Failure Repair

## ILF-001

`tests.operations.test_clean_machine_bootstrap.CleanMachineBootstrapScriptTests.test_bootstrap_creates_temp_checkout_and_validates_instance`

Root cause: the LOCAL-13 clean-machine bootstrap creates a filtered non-git temp copy at `eureka-clean-machine-*/checkout` and initializes `checkout/eureka-instance`. INSTANCE-LAYOUT-01 rejected that as repo-nested before recognizing it as ephemeral proof state.

Repair: the shared path resolver now recognizes only the LOCAL-13 non-git temp-copy harness shape while continuing to reject normal repo-nested instance roots.

## ILF-002

`tests.operations.test_clean_machine_smoke.CleanMachineSmokeScriptTests.test_validator_passes_with_known_warning`

Root cause: the validator reused the same temp checkout instance for local server smoke, so server startup failed through the shared resolver.

Repair: the same resolver compatibility path allows runtime status and local server startup to use the ephemeral clean-machine proof instance.

Changed files:

- `runtime/local_appliance/paths.py`
- `tests/runtime/test_local_appliance_paths.py`
