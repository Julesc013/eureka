# Review / Index Boundary Proof

## Accepted Inclusion

The persisted artifact contains only the accepted local fixture record:

- review status: `accepted`
- review decision id: `rvd_fixture_demo_project_accept_v0`
- indexed object id: `pir_f4453ae8f3ab6d41`

## Non-Accepted Exclusion

The artifact validator rejects records whose `review_status` is not `accepted`, and persisted artifact search refuses invalid artifacts. Existing Q59 tests also prove rejected review decisions are not indexed into the reviewed local index.

## Local / Public Boundary

- Artifact kind: `local_reviewed_fixture_index_candidate`
- `production_public_index: false`
- `public_index_mutation: false`
- Artifact path is under `.aide/queue/EUREKA-REVIEWED-INDEX-PERSISTENCE-01/evidence/fixture-run/`.
- No production public index path is written.

## Test Refs

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_rejected_review_decision_is_not_indexed`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_reviewed_index_artifact_reports_missing_corrupt_and_nonaccepted_records`
