# Source Observation Runtime Reference

This reference documents the public Python API added in R0-04.

## SourceId

`SourceId(value)` validates stable lowercase source identifiers. Valid identifiers start with a letter and may contain lowercase letters, numbers, dots, underscores, or hyphens.

## SourceRecord

`SourceRecord` describes a metadata source:

- `source_id`
- `source_family`
- `trust_lane`
- `label`
- `locators`
- `capabilities`
- `limitations`
- `metadata`

It supports `to_dict()`, `to_json()`, `from_dict()`, and `from_json()`.

## SourcePolicy

`SourcePolicy` describes allowed, blocked, and review-bound operations. Default blocked operations include live network requests, source sync, downloads, uploads, execution, private source access, registry mutation, and public index writes.

`evaluate_source_policy(record, requested_operation, context=None)` returns a `PolicyDecision`.

## PolicyDecision

`PolicyDecision` has one of four statuses:

- `allowed`
- `blocked`
- `requires_review`
- `not_evaluable`

Each decision includes the requested operation, reason, source id, and limitations.

## MetadataRequest

`MetadataRequest` describes an intended metadata observation. It does not execute the observation. Use `MetadataRequest.build(...)` to create a deterministic request id.

## MetadataResponse

`MetadataResponse` describes payload material already supplied by the caller. It computes a `ResponseFingerprint` from explicit payload text, bytes, or mapping data. It does not fetch endpoints or read files.

## SourceObservation

`SourceObservation` records observed fields, the response fingerprint, confidence, limitations, and warnings. It does not write to a cache or public index.

## NormalizedObservation

`NormalizedObservation` contains candidate normalized fields derived from a metadata response. `normalize_metadata_response(response, source_record, policy=None)` produces this object.

## EvidenceCandidate

`EvidenceCandidate` is created by `build_evidence_candidate(observation)`. It has `accepted=false` at creation and cannot represent accepted evidence.

## ReviewItem

`ReviewItem` is created by `build_review_item(candidate)`. It starts in `needs_review` and does not make a review decision.

## ConnectorHealth

`ConnectorHealth` summarizes source adapter health without performing checks itself. It records source id, status, checked time, observation count, warnings, and errors.

## Validation Helpers

The package exposes validation helpers for records, requests, responses, observations, normalized observations, evidence candidates, and reserved vocabulary.
