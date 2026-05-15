# Rebuild Determinism Proof

## Method

The runtime test runs the fixture slice twice in separate temporary roots, then compares both persisted reviewed-index artifact files byte-for-byte.

## Result

- Two independent rebuilds produce byte-identical `reviewed-index-artifact.json` files.
- Parsed artifact payloads are equal across runs.
- Artifact content hash is stable: `sha256:8c96ea8acf85da7c4ce1b40cc3dcd95edd6fa6c54105f75665f6ca79ec3ede23`.
- Artifact file SHA-256 is stable: `950c42873a2bcfeeac41854821eb27327b819ed09b710d233d88bb5c05999445`.

## Test Refs

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_reviewed_index_artifact_is_persisted_and_rebuilds_byte_identically`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_fixture_ids_are_deterministic_across_runs`

## Remaining Nondeterminism

The broader fixture report still contains transient SQLite migration timestamps from local stores. Q61 persistence intentionally isolates the deterministic artifact from those transient report timestamps.

