# Indexless Live Search Fallback Spec

## Purpose

Implement fallback only when local index data is unavailable or insufficient,
and only as a ResolutionRunKernel mode.

## Required Path

```text
query
-> ResolutionRunKernel
-> local lookup unavailable / insufficient
-> bounded fallback WorkUnit
-> source adapter
-> SourceObservation
-> EvidenceCandidate or SearchNeed
-> public-safe view model
```

## Required Controls

- source allowlist
- run budget
- timeout budget
- fallback disable switch
- source disable switch
- policy block state
- candidate/need output only
- replayable run events
- operator-visible diagnostics

## Non-Goals

No UI direct source call, arbitrary fanout, full Archive.org integration,
downloads, file fetching, extraction, execution, rights clearance, malware
proof, or reviewed truth mutation.

## Test Plan

- index unavailable creates fallback run
- local insufficient creates fallback run if allowed
- source allowlist denial creates `policy_blocked`
- budget exhaustion creates honest partial or unavailable state
- fallback-derived public result is not `verified`
- disable switch blocks fallback cleanly

