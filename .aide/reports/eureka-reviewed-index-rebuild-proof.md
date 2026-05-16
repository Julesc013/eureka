# Eureka Reviewed Index Rebuild Proof

The persisted reviewed fixture index artifact is deterministic across independent fixture runs.

## Proof

- Runtime test: `test_reviewed_index_artifact_is_persisted_and_rebuilds_byte_identically`
- Method: run the fixture slice in two separate temporary roots and compare `reviewed-index-artifact.json` bytes.
- Result: PASS.

## Stable Artifact

- Schema: `eureka.fixture_reviewed_index_artifact.v0`
- Artifact id: `ria_fixture_demo_project_v0`
- Artifact hash: `sha256:8c96ea8acf85da7c4ce1b40cc3dcd95edd6fa6c54105f75665f6ca79ec3ede23`
- File SHA-256: `950c42873a2bcfeeac41854821eb27327b819ed09b710d233d88bb5c05999445`

## Scope

The deterministic artifact is local fixture/test evidence. It is not production public-index state and does not perform live source access.
