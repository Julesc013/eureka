# Public Data Contract Stability Review v0

Public Data Contract Stability Review v0 classifies Eureka's generated static
public data fields before native, relay, snapshot-consumer, or other clients
start depending on them.

This is contract-governance only. It does not change runtime product behavior,
add live APIs, add live backend behavior, add live probes, deploy anything,
implement relay/native/snapshot-reader behavior, or claim production API
stability.

The review covers the six generated JSON files under `public_site/data/`:

- `site_manifest.json`
- `page_registry.json`
- `source_summary.json`
- `eval_summary.json`
- `route_summary.json`
- `build_manifest.json`

Primary outputs:

- `FIELD_STABILITY_MATRIX.md`
- `FILE_STABILITY_DECISIONS.md`
- `VERSIONING_POLICY.md`
- `BREAKING_CHANGE_POLICY.md`
- `CLIENT_CONSUMPTION_GUIDANCE.md`
- `public_data_stability_report.json`

The immediate next Codex-safe milestone is Generated Artifact Drift Guard v0.
Manual Observation Batch 0 Execution remains human-operated.
