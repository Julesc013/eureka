# Snapshot Local Apply Live Metadata Handoffs

The local-apply handoff is the only input that lets reviewed metadata/source-lead previews appear as limited reviewed records in `SNAPSHOT-REFRESH-03`.

The handoff records temp explicit instance proof only. It does not prove operator instance mutation, public publication, artifact verification, download availability, malware status, or rights clearance.

Snapshot refresh consumes:

- `control/inventory/local_apply_live_metadata_result.json`
- `examples/local_apply/live_metadata/reviewed_metadata_records.json`
- `examples/local_apply/live_metadata/reviewed_source_leads.json`
- `examples/local_apply/live_metadata/snapshot_refresh_handoff.json`

The output remains read-only projection evidence for the next public alpha reassessment.
