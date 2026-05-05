# Dry-Run Output Model

The CLI emits a deterministic JSON report with:

- `report_id`
- `mode: local_dry_run`
- `input_roots`
- `candidates_seen`
- `candidates_valid`
- `candidates_invalid`
- `candidate_summaries`
- `evidence_kinds`
- `claim_kinds`
- `source_families`
- provenance, review, privacy, public-safety, rights/risk, and promotion counts
- `mutation_summary`
- `warnings`
- `errors`
- `hard_booleans`

Hard booleans keep `local_dry_run: true` and keep all live source, external
call, connector, source-sync, authoritative write, mutation, public-search,
truth-acceptance, promotion, telemetry, credential, download, install, and
execution flags false.
