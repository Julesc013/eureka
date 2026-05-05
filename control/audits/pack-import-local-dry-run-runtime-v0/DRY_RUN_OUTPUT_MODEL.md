# Dry-Run Output Model

The CLI emits a JSON report with:

- `report_id`
- `mode: local_dry_run`
- `input_roots`
- `packs_seen`
- `packs_valid`
- `packs_invalid`
- `pack_summaries`
- `pack_kinds`
- `schema_versions`
- `validation_status_counts`
- `privacy_status_counts`
- `public_safety_status_counts`
- `risk_status_counts`
- `mutation_impact_counts`
- `promotion_readiness_counts`
- `dry_run_effects`
- `mutation_summary`
- `warnings`
- `errors`
- `hard_booleans`

Hard booleans keep local dry-run true and authoritative import, staging,
quarantine writes, promotion, accepted records, pack execution, URL following,
external calls, live calls, cache/ledger/index mutations, public contribution
intake, upload/admin endpoints, telemetry, credentials, downloads, installs,
and execution false.
