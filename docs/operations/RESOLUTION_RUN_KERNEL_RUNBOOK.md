# Resolution Run Kernel Runbook

Smoke the headless kernel:

```text
python scripts/eureka_resolution_run.py --query sampleproject --projection operator_workbench --json
python scripts/eureka_resolution_run.py --query sampleproject --projection public_web --json
python scripts/eureka_resolution_run.py --query sampleproject --projection native_desktop_read_only --json
```

Validate the foundation:

```text
python scripts/validate_resolution_run_kernel.py
python -m unittest tests.runtime.test_resolution_run_kernel
python -m unittest tests.operations.test_resolution_run_scripts
```

Expected posture:

- run state reaches `completed` for dry-run proof
- IA-Hunt WorkUnits are planned, not live-executed
- lane snapshots are projection-safe
- unsafe commands are blocked
- boundary flags remain false

Do not use this foundation to enable live IA metadata, downloads, extraction,
review promotion, or instance mutation. Those require later explicit gates.
