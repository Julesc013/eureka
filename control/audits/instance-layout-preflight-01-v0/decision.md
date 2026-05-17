# Decision

Decision: `commit_preflight`

Reason:

- The dirty files are documentation-only.
- The preferred default is the sibling `../instances/default` layout.
- The older `./eureka-instance` path is retained only as legacy validation
  fixture context, not as the recommended local development default.
- No runtime, script, test, instance, source-probe, extraction, model/provider,
  or deployment behavior is changed.

Next task remains:

`INSTANCE-LAYOUT-01 - Standardize sibling instances/default layout for local appliance runtime state`
