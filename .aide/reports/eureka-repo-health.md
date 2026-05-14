# Eureka Repo Health

## Current Queue

- Completed item: HUNT-01 - Search Hunt Session runtime.
- Current recommended item: HUNT-02 - Search Hunt UI state in Local Workbench.
- Alternative next item: SYN-00 - Synthetic Query Foundry planning over Local Appliance.
- F0 status: resumable through the Local Appliance, but deferred behind the HUNT baseline unless explicitly chosen.

## Local Appliance State

The final state packet records `main == dev`, zero hard blockers, full unittest discovery passing, and a runnable Local Appliance baseline. HUNT uses that baseline as the required product kernel.

## HUNT State

HUNT-00 inserted the planning/control spine. HUNT-01 adds durable Search Hunt Session runtime with a manifest-backed `search_hunt` SQLite store, runtime API, CLI, demo, validator, tests, inventories, docs, and audit evidence. HUNT-02 should expose that state in the Local Workbench.

## Boundaries

- WorkUnit creation from hunts: not enabled.
- Source probes: not executed.
- Extraction: not executed.
- Model/provider calls: not performed.
- Review mutation: not performed.
- Public/master index mutation: not performed.
- Site/dist mutation: not performed.
- Deployment: not performed.
- Production readiness: not claimed.
- Public launch readiness: not claimed.

## Warnings

The final baseline still records non-blocking warning debt: exact runtime leakage warning entries with zero new unallowlisted production findings, AIDE optional-reference warnings, and no external second-device LAN proof. These do not block HUNT-02.
