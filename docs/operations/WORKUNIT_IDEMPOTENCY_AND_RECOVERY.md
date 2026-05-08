# WorkUnit Idempotency And Recovery

This operations note records how Track B WorkUnits must behave when inspected,
validated, replayed, or resumed.

## Required Idempotency

- `safe_to_rerun`: true
- complete duplicate: `validate_and_record_noop`
- partial duplicate: `resume_from_missing_acceptance`
- conflicting duplicate: `classify_and_quarantine`

## Required Recovery

- dirty tree: `inspect_preserve_and_continue`
- missing dependency: `repair_if_bounded_else_record_blocker`
- stale status: `reconcile_from_evidence`
- failed validation: `repair_if_in_scope_else_record_blocker`
- out-of-order task: `inspect_queue_and_resume_valid_next`
- repeated prompt: `classify_noop_resume_or_repair`

## Stop Conditions

Stop and record a blocker for destructive ambiguity, missing external
credentials, legal or licensing decisions, manual observation requirements,
irreversible action without approval, private data exposure risk, unsafe
network or source action, or production deployment/hosting mutation.

## No-Goals

This policy does not execute WorkUnits, open browsers, fetch sources, call
providers, create local state, import packs, run reviews, or mutate the
master-index.
