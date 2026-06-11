# Attachment Decision

## Decision

```text
DECISION: WIRE_EXISTING_IA_TRANSPORT_THROUGH_ENGINE_FALLBACK
```

## Attachment Point

```text
query
-> LocalResolutionRunService._run_search
-> local lookup miss
-> LocalResolutionRunService._run_indexless_fallback
-> ResolutionRunFallbackPolicy
-> ArchiveOrgMetadataCandidateProvider with fixture transport
-> fallback_summary
-> SurfaceKernel resolution_run projection
-> json_v0 / text_v0 / html_basic_v0 / snapshot_v0
```

## Why This Is Safe

The engine already had a structural fallback provider protocol and policy gate.
The implementation adds no broad source framework and no public route source
call. The IA metadata provider is exercised with deterministic fixture transport
only.

One narrow engine behavior was added: a provider-declared `near_miss` fallback
state is preserved as `near_miss` instead of being collapsed to unavailable.

