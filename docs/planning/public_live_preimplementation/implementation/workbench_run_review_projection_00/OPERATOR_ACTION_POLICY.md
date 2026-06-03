# Operator Action Policy

Workbench action posture is private/operator scoped.

## Operator-Only Actions

```text
inspect_run
inspect_fallback_summary
inspect_candidate
inspect_need
create_review_item_from_candidate
create_review_item_from_need
review_candidate
promote
reject
supersede
mark_near_miss
mark_need
mark_policy_blocked
request_more_evidence
inspect_review_event
```

## Public-Disallowed Actions

```text
review_candidate
promote
reject
supersede
mark_need
mark_near_miss
mark_policy_blocked
request_more_evidence
rebuild_index
```

## Enablement Rules

| Action | Enabled When |
|---|---|
| `inspect_run` | Always in operator projection |
| `inspect_fallback_summary` | A fallback summary exists |
| `inspect_candidate` | Fallback status is `candidate` |
| `inspect_need` | Fallback status is `need` |
| `create_review_item_from_candidate` | Candidate fallback exists and no review item exists |
| `create_review_item_from_need` | Need fallback exists and no review item exists |
| `review_candidate` | Candidate fallback has a review item |
| Review ledger decisions | A review item exists |
| `inspect_review_event` | Ledger audit events exist |

All operator actions report:

```text
mutates_reviewed_record = false
mutates_reviewed_index = false
mutates_public_index = false
mutates_master_index = false
```

Only explicit review-item creation mutates review queue state.
