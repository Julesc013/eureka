# Drift Repair Report

Status: `BLOCKED_GENUINE_REGRESSION`

## Summary

The repair pass investigated the two unknown failure groups before changing
historical validators.

The local-worker unknown is now understood as historical queue expectation drift:
the local-worker runtime checks pass, but its validator still expects the old
`LOCAL-09` successor posture.

The runtime leakage unknown is a material blocker. The current runtime leakage
validator reports 52 new unallowlisted production-path findings and the targeted
runtime leakage test lane fails with two current-repo failures.

Because this validation-drift task protects runtime product paths, no runtime
leakage repair was attempted here.

## Why No External Rerun Was Prepared

The task requires all unknown groups to be resolved and targeted lanes to be
green before a new external full-discovery handoff is prepared.

That condition is not met:

- runtime leakage is failing in current-repo validation
- local-worker historical queue drift remains unrepaired
- HUNT/LOCAL/promotion/repo-layout/public-alpha/IA/staging historical drift
  groups remain unrepaired

Main promotion remains blocked.

## Safety Posture

- full discovery inside AI session: false
- external rerun handoff prepared: false
- dev-to-main promotion: false
- reviewed records created: false
- reviewed/master mutation: false
- public-index mutation: false
- network/provider calls: false
- downloads/file fetches: false
- public exposure: paused
- license posture: unchanged

## Recommended Next Action

Create and run a narrow runtime leakage repair task:

```text
SOURCE-FOUNDRY-RUNTIME-LEAKAGE-REPAIR-00
```

After that task clears the runtime leakage gate, resume historical drift repair
for the queue/validator groups.

