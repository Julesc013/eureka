# Index Validation Proof

## Validation Fields Checked

`validate_reviewed_index_artifact` checks:

- schema version;
- artifact id and artifact kind;
- local-only and fixture-only markers;
- `production_public_index: false`;
- `public_index_mutation: false`;
- no-live flags for network, provider/model, live source probes, and source sync;
- record count consistency;
- required source/evidence/review refs;
- accepted-only record status;
- surface packet schema;
- bounded absence metadata;
- deterministic artifact hash.

## Negative Behavior

Tests prove controlled handling for:

- missing artifact path: raises a rebuild-instruction `ValueError`;
- corrupt JSON artifact: raises a JSON validation `ValueError`;
- non-accepted record inside the artifact: validation fails and search refuses the artifact.

## Test Refs

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_reviewed_index_artifact_reports_missing_corrupt_and_nonaccepted_records`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_validate_report_rejects_mismatched_refs_and_mutation_flags`

