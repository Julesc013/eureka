# IA-HUNT-BRIDGE-00 Audit Pack

This audit pack records the local IA metadata to Hunt/WorkUnit/result-lane bridge proof.

The bridge is fixture-backed by default, creates dry-run WorkUnits without writes, and limits write proof to an explicit temporary instance. It does not enable live IA calls, source probes, downloads, extraction, model/provider calls, deployment, master-index mutation, operator-instance mutation, or public launch claims.

Key evidence:

- `ia_hunt_bridge_report.json`
- `workunit_schema.md`
- `pipeline_matrix.md`
- `result_lane_matrix.md`
- `smoke_result.md`
- `validation_matrix.md`
- `boundary_report.md`
- `validation.md`
- `generated/full_unittest_summary.txt`
