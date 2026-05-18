# IA Review Decision

IA-06 review decisions classify provisional IA candidates for local review.
They are not final truth and do not write reviewed or master indexes.

Allowed decisions:

- `approve_for_reviewed_index_dry_run`
- `reject_candidate`
- `needs_more_evidence`
- `mark_near_miss`
- `mark_duplicate`
- `mark_policy_blocked`
- `mark_rights_risk`
- `mark_safety_risk`

`approve_for_reviewed_index_dry_run` may create a promotion preview. The
preview remains preview-only and does not write a reviewed record.

Required invariants:

- rationale is required
- `accepted_truth` is false
- reviewed and master index mutation flags are false
- `raw_response_committed` is false
- `download_performed` is false

