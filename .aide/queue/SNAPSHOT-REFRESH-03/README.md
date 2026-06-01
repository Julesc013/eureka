# SNAPSHOT-REFRESH-03

Status: planned

Refresh snapshots after local apply of live metadata previews.

Inputs:

- `control/inventory/local_apply_live_metadata_result.json`
- `examples/local_apply/live_metadata/reviewed_metadata_records.json`
- `examples/local_apply/live_metadata/reviewed_source_leads.json`
- `examples/local_apply/live_metadata/snapshot_refresh_handoff.json`

Boundary:

- package limited reviewed metadata/source-lead records
- do not create verified-download, malware-clean, or rights-clearance claims
- do not mutate public/master indexes
- do not deploy or claim launch readiness
