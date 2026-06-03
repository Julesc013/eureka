# Workbench Projection Map

## Projection Entry Point

```text
runtime/local/service/workbench_run_review_projection.py
project_workbench_run_review(...)
```

## Input Mapping

| Input | Workbench Projection |
|---|---|
| `ResolutionRunRecord.run_id` | `run.run_id` |
| `ResolutionRunRecord.run_kind` | `run.run_kind` |
| `ResolutionRunRecord.requested_value` | `run.requested_value` |
| `ResolutionRunRecord.result_summary` | `run.result_kind`, `run.result_count`, `local_lookup.status` |
| `ResolutionRunRecord.absence_report` | `local_lookup.absence_report_present` |
| `ResolutionRunRecord.fallback_summary` | `fallback_summary` |
| `fallback_summary.candidates` | `fallback_summary.candidates[*]` as `candidate`, never verified |
| `fallback_summary.needs` | `fallback_summary.needs[*]` as `need`, never verified |
| `fallback_summary.status=policy_blocked` | visible policy-blocked fallback state |
| `fallback_summary.status=unavailable` | visible unavailable/degraded fallback state |
| `ReviewQueueStore.review_items` | `review_ledger.review_items` |
| `ReviewQueueStore.review_decisions` | `review_ledger.decisions` |
| `ReviewQueueStore.review_events` | `review_ledger.audit_events` |

## Local Lookup States

| Condition | Projected State |
|---|---|
| Result summary has results | `reviewed_result_available` |
| Fallback trigger is `local_lookup_unavailable` | `local_lookup_unavailable` |
| Fallback exists after no result | `local_lookup_insufficient` |
| Absence report exists without fallback | `local_lookup_no_results` |
| None of the above | `unknown` |

## Output Non-Claims

Every fallback item and source observation is projected with:

```text
verified = false
accepted_truth = false
reviewed_record_created = false
reviewed_index_mutated = false
public_index_mutated = false
master_index_mutated = false
```
