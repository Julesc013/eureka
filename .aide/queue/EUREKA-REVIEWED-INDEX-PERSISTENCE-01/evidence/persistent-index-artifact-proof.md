# Persistent Index Artifact Proof

## Artifact

- Path: `.aide/queue/EUREKA-REVIEWED-INDEX-PERSISTENCE-01/evidence/fixture-run/reviewed-index-artifact.json`
- Schema: `eureka.fixture_reviewed_index_artifact.v0`
- Artifact id: `ria_fixture_demo_project_v0`
- Builder id: `eureka.fixture_reviewed_index_persistence.v0`
- Artifact hash: `sha256:8c96ea8acf85da7c4ce1b40cc3dcd95edd6fa6c54105f75665f6ca79ec3ede23`
- Artifact file SHA-256: `950c42873a2bcfeeac41854821eb27327b819ed09b710d233d88bb5c05999445`
- Record count: 1
- Indexed object ids: `pir_f4453ae8f3ab6d41`

## Shape

The artifact includes schema/version, generated-by metadata, stable fixture timestamp, source fixture id, source observation refs, evidence refs, review refs, accepted indexed records, surface packet refs, absence metadata, no-live flags, fixture/local-only markers, and explicit `production_public_index: false`.

## Refs

- Source id: `source.fixture.local.metadata`
- Source observation id: `obs_f784e76abbff8837`
- Normalized observation id: `norm_c8d2a070b535533a`
- Source cache entry id: `sce_166f90a6738492c5`
- Evidence id: `evc_7a58fa86edc377ef`
- Review item id: `rvi_eba5b8afd11a4cf4`
- Review decision id: `rvd_fixture_demo_project_accept_v0`

## Test Refs

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_reviewed_index_artifact_is_persisted_and_rebuilds_byte_identically`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_reviewed_index_artifact_loads_and_serves_search_object_and_absence`
- Fixture run report: `.aide/queue/EUREKA-REVIEWED-INDEX-PERSISTENCE-01/evidence/fixture-run-report.json`

