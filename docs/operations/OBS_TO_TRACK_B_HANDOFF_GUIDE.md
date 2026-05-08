# OBS To Track B Handoff Guide

## What The Handoff Is

The OBS to Track B handoff is a review process for draft observation outputs. It tells a human reviewer and later Track B tasks which OBS artifacts are ready for review, which are blocked, and which Track B dependencies must exist before runtime consumption.

It is not an approval record and it is not a runtime queue.

## Handoff Inputs

- ObservationCandidate records and candidate manifests.
- Observation candidate review queue entries.
- Source gap candidate manifests.
- SearchNeed seed manifests.
- WorkUnit seed manifests.
- Manual observation pending-slot metadata.
- Track B node, policy, capability, WorkUnit, WorkUnit result, and local foundry state contracts.

## Human Review

Human review is required before a candidate, SearchNeed seed, or WorkUnit seed is consumed downstream. A reviewer may approve a draft for future conversion, request more evidence, mark it duplicate, defer it, or keep it policy-blocked.

Approving a draft for future conversion does not make it observed baseline evidence. It does not make it accepted evidence truth. It does not mutate the master index.

## Source Policy

Source policy approval remains separate. A source lead can be useful and still remain blocked. Source policy review must happen before live source access, source sync, source connectors, or live probes are planned as executable work.

## SearchNeed Seeds

SearchNeed seeds are draft needs. They can help Track B decide what kind of search or observation work should exist later, but they are not runtime SearchNeed records until Track B defines and accepts that runtime path.

## WorkUnit Seeds

WorkUnit seeds are draft work proposals. They can describe bounded work that might later become Track B WorkUnits, but they are not executable WorkUnits and must not be run by the OBS lane.

## Runtime Activation

Runtime activation is allowed only after matching Track B contracts, runtime implementation, review gates, and policy gates exist. This sync audit cannot activate runtime behavior.

## Public Index Effects

Public index effects are not allowed from OBS handoff artifacts. Any public effect requires accepted evidence, explicit promotion rules, and the governed Track B or product path that owns that change.

## Validation

Use:

```text
python scripts/audit_obs_track_b_synchronization.py --check
python scripts/validate_obs_track_b_synchronization.py
python scripts/summarize_obs_track_b_handoff.py
```

## No-Goals

- No Track B contract or runtime mutation.
- No runtime SearchNeed creation.
- No executable WorkUnit creation.
- No WorkUnit execution.
- No source access approval.
- No external observation or live source access.
- No evidence acceptance.
- No master-index mutation.
