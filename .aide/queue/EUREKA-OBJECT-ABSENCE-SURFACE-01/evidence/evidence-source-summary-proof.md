# Evidence and Source Summary Proof

## Evidence Summary Packet

- Packet id: `esp_fixture_demo_project_v0`
- Schema: `eureka.evidence_summary_packet.v0`
- Evidence id: `evc_7a58fa86edc377ef`
- Claim type: `metadata`
- Subject id: `fixture.demo-project`
- Source id: `source.fixture.local.metadata`
- Review decision: `accepted`
- Accepted for local index: `true`
- Fixture/local-only markers: `true`

## Source / Provenance Packet

- Packet id: `spp_fixture_local_metadata_v0`
- Schema: `eureka.source_provenance_packet.v0`
- Source family: `local_fixture`
- Source reference: `fixture://q58/demo-project`
- Observed at: `2026-05-12T00:00:01Z`
- No-live flags: network calls false, provider/model calls false, live source probes false, source sync false.

## Test Refs

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_surface_packets_expose_result_object_evidence_source_and_absence`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_validator_reports_surface_packet_errors`

