# Eureka Repo Health

## Current Queue

- Completed item: LOCAL-14 - Local appliance closeout and F0/HUNT/SYN handoff.
- Current recommended item: HUNT-00 - Search Hunt track planning over Local Appliance.
- Alternative next item: SYN-00 - Synthetic Query Foundry planning over Local Appliance.
- F0 status: resumable through the Local Appliance, but not recommended before HUNT/SYN unless explicitly chosen.
- Compatibility note: `eureka-repo-health.json` keeps `current_queue_item` at the LOCAL-02 guard-compatible value used by the legacy LOCAL-00 validator; `.aide/queue/index.yaml` is the queue source of truth for HUNT-00.

## Local Appliance State

LOCAL-00 through LOCAL-14 now form the Local Appliance product kernel: explicit instance root, migration guard, runtime composition, localhost service, HTML workbench, hardened pages, WorkUnit queue, review/rebuild, deterministic workers, auto-test/search, LAN safety and smoke, clean-machine bootstrap, and closeout handoff.

## Boundaries

- HUNT can start planning over the Local Appliance.
- SYN can start planning over the Local Appliance.
- F0 can resume only through the Local Appliance and is not recommended immediately.
- Main promotion requires a separate LOCAL-TO-MAIN-PROMOTION-REVIEW task.
- Source probes: not executed.
- Extraction: not executed.
- Model/provider calls: not performed.
- Master index mutation: not performed.
- Site/dist mutation: not performed.
- Deployment: not performed.
- Production readiness: not claimed.
- Public launch readiness: not claimed.

## Warnings

The runtime leakage gate remains a pre-existing warning at 1030 findings. LOCAL did not increase leakage. The warning does not block HUNT/SYN/F0 planning but blocks automatic main promotion until LOCAL-LEAKAGE-01 or an equivalent review resolves it.
