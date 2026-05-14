# Eureka Repo Health

## Current Queue

- Completed item: LOCAL-LEAKAGE-TOTAL-REMEDIATION-01 - Total leakage remediation and final green gate.
- Current recommended item: HUNT-00 - Search Hunt track planning over Local Appliance.
- Alternative next item: SYN-00 - Synthetic Query Foundry planning over Local Appliance.
- F0 status: resumable through the Local Appliance, but not recommended before HUNT/SYN unless explicitly chosen.
- Compatibility note: `eureka-repo-health.json` keeps `current_queue_item` at the LOCAL-02 guard-compatible value used by the legacy LOCAL-00 validator; `.aide/queue/index.yaml` is the queue source of truth for HUNT-00.

## Local Appliance State

LOCAL-00 through LOCAL-14 are present and the total remediation sweep reran the LOCAL validators, local smokes, LAN smoke, clean-machine proof, architecture checks, generated-artifact gate, runtime leakage gate, and full unittest discovery.

## Boundaries

- HUNT can start planning over the Local Appliance.
- SYN can start planning over the Local Appliance.
- F0 can resume only through the Local Appliance and is not recommended immediately.
- Main promotion is allowed only through the explicit fast-forward promotion procedure.
- Source probes: not executed.
- Extraction: not executed.
- Model/provider calls: not performed.
- Master index mutation: not performed.
- Site/dist mutation: not performed.
- Deployment: not performed.
- Production readiness: not claimed.
- Public launch readiness: not claimed.

## Warnings

The runtime leakage gate has zero new unallowlisted production findings and 1954 exact, expiring warning entries. The remaining warning debt does not block HUNT/SYN/F0 or main promotion. AIDE verify still reports non-blocking stale context/diff-scope warnings for this superseding task.
