# Dry-Run Output Model

Dry-run output is a JSON report with:

- `report_id`
- `mode: local_dry_run`
- `input_roots`
- `candidates_seen`
- `candidates_valid`
- `candidates_invalid`
- `candidate_summaries`
- `source_families`
- `record_kinds`
- `privacy_status_counts`
- `public_safety_status_counts`
- `evidence_readiness_counts`
- `policy_status_counts`
- `mutation_summary`
- `warnings`
- `errors`
- `hard_booleans`

Hard booleans keep `local_dry_run` true and keep live calls, external calls,
connector execution, source-sync execution, authoritative writes, mutations,
public-search mutation, telemetry, credentials, downloads, installs, and
execution false.
