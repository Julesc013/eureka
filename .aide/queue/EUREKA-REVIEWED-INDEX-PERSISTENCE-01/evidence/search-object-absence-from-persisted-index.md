# Search / Object / Absence From Persisted Index

## Positive Search

- Query: `demo project`
- Function: `search_reviewed_index_artifact`
- Result count: 1
- Returned object id: `pir_f4453ae8f3ab6d41`
- Returned evidence id: `evc_7a58fa86edc377ef`
- Returned review decision id: `rvd_fixture_demo_project_accept_v0`

## Object Detail

- Function: `get_reviewed_index_artifact_object`
- Object id: `pir_f4453ae8f3ab6d41`
- Found: true
- Object/detail packet schema: `eureka.object_detail_packet.v0`
- Packet includes source, evidence, review, source-cache, and provenance refs.

## Absence

- Query: `zzznomatch`
- Function: `absence_from_reviewed_index_artifact`
- Result count: 0
- Checked index: `ria_fixture_demo_project_v0`
- Checked source: `source.fixture.local.metadata`
- Meaning: bounded local fixture artifact absence only.

## Test Refs

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_reviewed_index_artifact_loads_and_serves_search_object_and_absence`
- `tests/operations/test_fixture_source_observation_vertical_slice_script.py::test_validator_script_writes_report_and_prints_json`
- `tests/operations/test_fixture_source_observation_vertical_slice_script.py::test_validator_uses_default_temp_root`

