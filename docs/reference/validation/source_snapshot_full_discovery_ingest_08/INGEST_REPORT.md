# Ingest Report

## Status

`FAIL`

## External Run

```text
run_id: source_snapshot_full_discovery_rerun_08
status: fail
command: python -m unittest discover -s tests -t .
started_at: 2026-06-11T14:19:28Z
terminal_updated_at: 2026-06-11T15:09:23Z
duration_seconds: 2995.178363
```

## Counts

```text
tests_run: 5676
failures: 23
errors: 0
skipped: 0
exit_code: 1
```

## Currentness

```text
summary_branch: dev
summary_head: 7db32002d7c6ad16a8fb41967d4e43a2ed4bcc5b
current_head: 7db32002d7c6ad16a8fb41967d4e43a2ed4bcc5b
summary_current_to_head: true
summary_working_tree_clean: true
```

## Classification

The compact failure evidence reports 12 raw unittest failure families across 23
failed tests. These collapse into three validator-drift families:

- `historical_queue_validator_drift`
- `historical_dev_to_main_promotion_validator_drift`
- `public_alpha_defer_queue_validator_drift`

No runtime behavior repair was applied in this ingest.

## Boundary

This ingest records terminal external validation evidence only.

```text
full_discovery_run_inside_ai: false
public_alpha_launched: false
dev_to_main_promoted: false
artifact_evidence_created: false
verified_artifact_claims_created: false
reviewed_public_master_indexes_mutated: false
ia_metadata_provider_repaired: false
local_metadata_fallback_demo_attempted: false
```

