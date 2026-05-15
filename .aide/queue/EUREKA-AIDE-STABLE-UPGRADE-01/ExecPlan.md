# ExecPlan - Q55 Eureka Stable AIDE Upgrade

## Objective

Upgrade Eureka's existing `.aide/` control plane from the validated stable
AIDE Lite bundle while preserving Eureka-specific memory, queue evidence,
golden tasks, reports, architecture checks, validators, and product boundaries.

## Plan

1. Confirm repo identity, branch state, guard output, and Q54 readiness.
2. Validate the source release bundle and extract it outside the Eureka repo.
3. Build a preservation-first sync plan that excludes source memory, queues,
   generated context/reports, release dist artifacts, raw prompts/responses,
   secrets, and local state.
4. Apply only portable `.aide/` control-plane files and merge golden-task
   catalog entries without deleting target-specific tasks.
5. Regenerate Eureka-local AIDE outputs where safe and supported.
6. Run AIDE validation, architecture boundary validation, git checks, and a
   targeted secret scan.
7. Write Q55 evidence, leave status at `needs_review`, and commit only safe
   Q55/AIDE changes if validation supports it.

## Boundaries

No product roots, source/evidence/index product state, scripts, tests, runtime,
contracts, surfaces, site, snapshots, native/crates, branches, tags, remotes,
providers, model calls, crawlers, live probes, or release publishing are in
scope.
