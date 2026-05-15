# Worker Runner Summary

LOCAL-09 adds `runtime/local_worker` and the `eureka_worker_runner.py` CLI.

The runner:

- opens the local instance through `runtime/local_appliance`
- fetches queued WorkUnits from `workunit_queue`
- evaluates worker policy before execution
- transitions queued records through running to complete, failed, or blocked
- records worker result and audit references
- keeps risky worker kinds disabled

The reviewed-index rebuild worker is enabled but token-gated. Other enabled workers are read-only or noop-style local operations.
