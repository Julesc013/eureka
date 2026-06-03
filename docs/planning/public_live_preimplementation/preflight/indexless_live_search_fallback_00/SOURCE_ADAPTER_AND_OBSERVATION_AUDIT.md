# Source Adapter And Observation Audit

## Source Family Abstraction

Present.

Relevant paths:

- `runtime/source/registry/**`
- `runtime/source/action/action_kernel.py`
- `runtime/source/action/source_wave.py`
- `runtime/connectors/**`
- `contracts/source/families/**`

Current behavior:

- Source records and source families exist.
- Source action manifests require `default_enabled=false`,
  `public_fanout_allowed=false`, downloads/extraction disabled, and
  `review_required=true`.
- SourceWave adapters provide fixture/action families.

## IA Metadata Adapter

Present.

Relevant paths:

- `runtime/source/observation/archive_org_public_metadata.py`
- `runtime/source/observation/internet_archive_live_probe.py`
- `runtime/source/observation/internet_archive_live_transport.py`
- `runtime/source/observation/internet_archive_candidate_index.py`

Current behavior:

- `ArchiveOrgMetadataCandidateProvider` performs bounded metadata-only
  Archive.org advancedsearch calls.
- It caps rows, uses one request per search, records flags such as
  `live_call_performed`, `raw_response_committed=false`,
  `accepted_truth=false`, and `review_required=true`.
- The IA live probe path requires explicit approval and validates policy caps.

Risk:

- `ArchiveOrgMetadataCandidateProvider` is currently injectable into
  `runtime/gateway/public_api/public_search.py`. For fallback, wrap it behind
  the engine resolution-run service rather than expanding public search as the
  source-calling layer.

## Source Observation Record

Present in several shapes.

Relevant paths:

- `contracts/source/action/source_observation_envelope.v0.json`
- `contracts/runtime/source/observation.v0.json`
- `runtime/source/action/action_kernel.py`
- `runtime/source/observation/**`

Current behavior:

- Source action normalization creates a `source_observation_envelope.v0`.
- Observation and candidate code keeps `accepted_truth=false` and
  `review_required=true`.
- IA observation cache/evidence/candidate/review flows preserve source refs and
  do not self-promote.

## Source Cache

Present for IA and local flows.

Relevant paths:

- `runtime/source/observation/internet_archive_source_cache.py`
- `contracts/stores/source_cache_status.v0.json`

Fallback should not require persistent source cache writes in the first slice.
If cache plans are created, they must remain plan-only unless a later task
explicitly enables a governed store write.

## Source Policy

Present but distributed.

Relevant paths:

- `runtime/source/observation/policy.py`
- `runtime/source/action/action_kernel.py`
- `control/policies/*source*`
- `runtime/source/observation/internet_archive_live_probe.py`

Implementation must add or assemble a single fallback policy check inside the
engine run path.

## Source Disable Switch

Partial.

Existing controls:

- source action manifests `default_enabled=false`
- source policies block live/source sync/download/private operations
- IA live probe `kill_switch_enabled`
- public search `source_policy`

Gap:

- no central per-source-family fallback disable switch in
  `LocalResolutionRunService`.

## Adapter Test Fixtures

Present.

Relevant tests:

- `tests/runtime/test_source_action_kernel.py`
- `tests/runtime/test_source_action_resolution_run_integration.py`
- `tests/runtime/test_source_wave_resolution_run_integration.py`
- `tests/runtime/test_archive_org_public_metadata_candidates.py`
- `tests/runtime/test_ia_candidate_*`
- connector live-probe and review-integration tests

## Implementation Reuse

Reuse:

- source action policy and non-claim fields
- Archive.org metadata candidate provider as a bounded adapter
- candidate normalization and boundary reports
- source observation envelopes where compatible

Add:

- engine-run scoped fallback policy/config
- source allowlist
- run output lane/notice shape for fallback candidate/need/degraded state
