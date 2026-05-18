# Review Policy

IA-06 review queue writes are enabled only for an explicit temporary or local
instance. Dry-run is the default and `--apply` plus a configured operator token
is required for mutation.

Allowed decisions:

- `approve_for_reviewed_index_dry_run`
- `reject_candidate`
- `needs_more_evidence`
- `mark_near_miss`
- `mark_duplicate`
- `mark_policy_blocked`
- `mark_rights_risk`
- `mark_safety_risk`

Review decisions are local classifications. They do not create accepted truth,
reviewed-index writes, or master-index writes.

