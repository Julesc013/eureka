# Queue Lifecycle Model

Allowed statuses include `draft_example`, `dry_run_validated`,
`queued_future`, `approval_required`, `operator_required`, `blocked_by_policy`,
`superseded_future`, `completed_future`, and `cancelled_future`.

P63 examples are not runtime queue records. Future lifecycle movement requires a
separate runtime/storage contract, approval policy, and safety evidence.
