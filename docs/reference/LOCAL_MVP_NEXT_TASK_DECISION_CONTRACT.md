# Local MVP Next Task Decision Contract

`local_mvp_next_task_decision.v0` records the selected next local task and the alternatives considered. Current decisions must keep `deployment_allowed_current` and `launch_allowed_current` false.

The contract can select H2, remediation, or a blocked route. It must not route to deployment execution without a future explicit operator approval artifact.
