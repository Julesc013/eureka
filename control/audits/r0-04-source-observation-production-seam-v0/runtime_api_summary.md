# Runtime API Summary

Public API:

- `SourceId`
- `SourceRecord`
- `SourceCapability`
- `SourceLocator`
- `SourcePolicy`
- `PolicyDecision`
- `PolicyDecisionStatus`
- `MetadataRequest`
- `MetadataResponse`
- `ResponseFingerprint`
- `SourceObservation`
- `NormalizedObservation`
- `EvidenceCandidate`
- `ReviewItem`
- `ReviewStatus`
- `ConnectorHealth`

Public functions:

- `evaluate_source_policy`
- `build_source_observation`
- `normalize_metadata_response`
- `build_evidence_candidate`
- `build_review_item`
- validation helpers for source records, metadata requests, metadata responses, observations, normalized observations, evidence candidates, and reserved vocabulary

The package does not import existing connector modules or network/provider libraries.
