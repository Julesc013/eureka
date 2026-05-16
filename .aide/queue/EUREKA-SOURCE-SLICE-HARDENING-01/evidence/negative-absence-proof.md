# Negative / Absence Proof

Absence path:

- Query: `zzznomatch`
- Result count: `0`
- Checked source: `source.fixture.local.metadata`
- Limitations:
  - local reviewed index only;
  - absence does not prove no matching source exists;
  - absence does not inspect live sources.

Rejected/non-accepted path:

- Q59 added `test_rejected_review_decision_is_not_indexed`.
- A rejected review decision is rebuilt with `included_count: 0` and `excluded_count: 1`.
- The produced local public index store has `record_count: 0`.
- Input source/evidence/review stores have matching SHA-256 digests before and after rebuild.

Malformed report path:

- Q59 added `test_validate_report_rejects_mismatched_refs_and_mutation_flags`.
- The validator rejects mismatched object/evidence refs, mutation flags, and live/network flags.

Test refs:

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_product_output_roots_are_rejected`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_validate_report_rejects_mismatched_refs_and_mutation_flags`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_rejected_review_decision_is_not_indexed`
- `tests/operations/test_fixture_source_observation_vertical_slice_script.py::test_validator_rejects_product_output_root`
