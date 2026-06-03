# Behavior Summary

## Review Inputs

The ledger can create review items from fallback summaries while stripping unsafe input fields such as direct accepted/public-index mutation flags from the stored review payload.

Supported fallback subjects:

- `fallback_candidate`
- `fallback_need`
- degraded fallback states such as `fallback_policy_blocked` or `fallback_unavailable`

## Review Decisions

Canonical ledger decisions map to existing queue decisions:

- `promote` -> accepted queue status and `verified` resulting status
- `reject` -> rejected
- `supersede` -> superseded
- `mark_near_miss` -> near-miss decision context without acceptance
- `mark_need` -> need
- `mark_policy_blocked` -> policy-blocked
- `request_more_evidence` -> need

## Required Boundary

Promotion requires:

- existing review item
- explicit actor
- local-only confirmation
- citation or rationale
- persisted review decision
- persisted review audit event

The ledger decision does not itself rebuild reviewed/public indexes.
