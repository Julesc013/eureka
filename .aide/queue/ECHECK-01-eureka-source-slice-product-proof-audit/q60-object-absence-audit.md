# Q60 Object / Absence Audit

## Result Packet

- Packet id: `srp_fixture_demo_project_v0`
- Schema: `eureka.search_result_packet.v0`
- Query: `demo project`
- Result count: 1
- Refs include object id, artifact id, source id/ref, evidence id, evidence
  summary id, review decision id, review status, fixture/local markers, and
  inspect actions.

## Object / Detail Packet

- Packet id: `odp_fixture_demo_project_v0`
- Schema: `eureka.object_detail_packet.v0`
- Object id: `pir_f4453ae8f3ab6d41`
- Refs include source observation, normalized observation, source cache,
  evidence, evidence summary, review item, review decision, and source
  provenance packet.

## Evidence Summary

- Packet id: `esp_fixture_demo_project_v0`
- Evidence id: `evc_7a58fa86edc377ef`
- Review decision: accepted for local index.

## Source / Provenance Summary

- Packet id: `spp_fixture_local_metadata_v0`
- Source family: `local_fixture`
- Source reference: `fixture://q58/demo-project`
- No-live flags: network false, provider/model false, live source probes false,
  source sync false.

## Absence Packet

- Packet id: `ap_fixture_zzznomatch_v0`
- Schema: `eureka.absence_packet.v0`
- Query: `zzznomatch`
- Result count: 0
- Meaning: bounded local fixture index absence only.

## Tests

Q60 packet behavior is covered by the runtime and operation fixture tests and
the validator report. ECHECK reran the latest Q61-expanded test file, which
retains Q60 assertions.

## Remaining Warnings

All packets remain fixture-only/local-only. There is no API surface, static
renderer, hosted UI, live source, or public index claim.

