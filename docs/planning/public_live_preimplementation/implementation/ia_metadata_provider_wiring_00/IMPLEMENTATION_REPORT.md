# Implementation Report

## Summary

The task adds fixture-backed IA metadata fallback smoke coverage for:

```text
candidate
need
near_miss
policy_blocked
unavailable
```

The implementation uses existing code where available:

```text
LocalResolutionRunService
ResolutionRunFallbackPolicy
ArchiveOrgMetadataCandidateProvider
SurfaceKernel
json_v0
text_v0
html_basic_v0
snapshot_v0
```

## Runtime Change

`runtime/engine/resolution_runs/service.py` now preserves a provider result
with status `near_miss` as a fallback summary with canonical status
`near_miss`.

## Fixture Smoke

The fixture smoke package lives at:

```text
evals/hard_queries/metadata_fallback_smoke/ia_00/
```

It contains query inputs, IA metadata fixtures, expected fallback outputs,
surface projection expectations, renderer expectations, and truth-boundary
reports.

