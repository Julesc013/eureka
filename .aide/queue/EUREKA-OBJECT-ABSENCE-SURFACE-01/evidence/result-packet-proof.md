# Result Packet Proof

## Positive Query

- Query: `demo project`
- Packet id: `srp_fixture_demo_project_v0`
- Schema: `eureka.search_result_packet.v0`
- Result count: `1`

## Fields Present

The result packet includes query, result count, object/result id, artifact id, title, version, source id, source reference, evidence summary ref, evidence id, review decision id, review status, confidence, matched terms, fixture/local-only markers, and inspect actions.

## Refs

- Object id: `pir_f4453ae8f3ab6d41`
- Artifact id: `fixture.demo-project`
- Source id: `source.fixture.local.metadata`
- Evidence id: `evc_7a58fa86edc377ef`
- Evidence summary packet id: `esp_fixture_demo_project_v0`
- Review decision id: `rvd_fixture_demo_project_accept_v0`

## Test Refs

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_surface_packets_expose_result_object_evidence_source_and_absence`
- `tests/operations/test_fixture_source_observation_vertical_slice_script.py::test_validator_writes_report`
- Fixture run report: `.aide/queue/EUREKA-OBJECT-ABSENCE-SURFACE-01/evidence/fixture-run-report.json`
