# Dry-Run Output Model

The CLI emits a deterministic JSON report with:

- `report_id`
- `mode: local_dry_run`
- `input_roots`
- `result_sets_seen`
- `result_sets_valid`
- `result_sets_invalid`
- `result_summaries`
- `current_order`
- `proposed_dry_run_order`
- `fallback_order`
- `ranking_factors`
- `factor_summary`
- `explanation_summaries`
- `conflict_gap_visibility_summary`
- `privacy_status_counts`
- `public_safety_status_counts`
- `eval_gate_summary`
- `warnings`
- `errors`
- `hard_booleans`

Hard booleans keep the boundary explicit: local dry-run is true, and public search ranking runtime, route/response/order changes, hosted runtime, hidden scores, suppression, model calls, AI reranking, telemetry, popularity, user-profile, ad signals, source/evidence reads, mutations, live calls, credentials, downloads, installs, and execution are false.

