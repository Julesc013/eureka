# Existing Runner Seams

Canonical orchestration owner:

- `runtime/resolution_run/run_kernel.py`
- `runtime/resolution_run/runner.py`
- `runtime/resolution_run/event_log.py`
- `runtime/resolution_run/run_store.py`
- `runtime/resolution_run/workunit_scheduler.py`
- `runtime/resolution_run/lane_projector.py`

Compatibility wrappers:

- `run_resolution_dry_run(...)`
- `scripts/eureka_resolution_run.py`
- `tools/generators/eureka_resolution_run.py`
- `runtime/local/service/workbench_live_run.py`

Provider-specific planning remains in adapters such as IA dry-run scheduling.
The runner core does not import or call live providers.

Disposition:

- retain the existing ResolutionRun kernel;
- extend it with ports, bundles, replay, and modes;
- keep Workbench as projection over the shared runner facade;
- do not create another Workbench-only or CLI-only lifecycle.
