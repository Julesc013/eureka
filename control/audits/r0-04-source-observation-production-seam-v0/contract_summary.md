# Contract Summary

R0-04 adds product-facing contracts:

- `contracts/domain/source_record.v0.json`
- `contracts/domain/source_policy.v0.json`
- `contracts/runtime/metadata_request.v0.json`
- `contracts/runtime/metadata_response.v0.json`
- `contracts/runtime/source_observation.v0.json`
- `contracts/runtime/normalized_observation.v0.json`
- `contracts/runtime/evidence_candidate.v0.json`
- `contracts/runtime/review_item.v0.json`
- `contracts/runtime/connector_health.v0.json`

These schemas describe product-domain and runtime boundaries only. They do not claim persistence, live source access, or review acceptance.

The R0-03 contract taxonomy scanner was updated narrowly so `contracts/runtime/evidence_candidate.v0.json` is treated as a runtime product contract despite the generic candidate-name rule used for legacy preview schemas.
