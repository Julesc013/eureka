# SNAPSHOT-REFRESH-03

Status: pass

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

Result:

- existing reviewed records: 1
- reviewed metadata records from local apply: 1
- reviewed source leads from local apply: 2
- reviewed record delta count: 3
- total limited reviewed record projection count: 4
- next task: `PUBLIC-ALPHA-REASSESS-03`
