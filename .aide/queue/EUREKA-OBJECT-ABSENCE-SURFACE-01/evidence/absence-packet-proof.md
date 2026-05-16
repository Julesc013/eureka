# Absence Packet Proof

## Absence Query

- Query: `zzznomatch`
- Packet id: `ap_fixture_zzznomatch_v0`
- Schema: `eureka.absence_packet.v0`
- Result count: `0`

## Bounded Meaning

The packet reports that no local reviewed fixture record matched the query. It records the checked source set and local reviewed index scope, and explicitly avoids global absence claims.

## Checked Scope

- Checked source: `source.fixture.local.metadata`
- Checked index: `isolated_fixture_reviewed_index`
- Known gaps:
  - local fixture index only;
  - does not inspect live sources;
  - does not prove global absence.

## Determinism

The full `surface_packets` object is asserted equal across two independent fixture-run reports in the runtime tests.

## Test Refs

- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_fixture_slice_report_is_deterministic`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py::test_surface_packets_expose_result_object_evidence_source_and_absence`
- `tests/operations/test_fixture_source_observation_vertical_slice_script.py::test_validator_uses_default_temp_root`
