# Candidate Promotion Dry-Run

Candidate promotion dry-run is a local, explicit-input runtime that evaluates whether a provisional candidate has enough fixture evidence and review queue approval to seed a future reviewed-record proposal.

It is not actual promotion. It does not accept candidates, accept evidence, create public records, write public indexes, mutate the master index, host moderation, fetch sources, call providers, or create private local state.

## Inputs

- candidate records from the Candidate Store
- evidence ledger candidate records
- local review queue entries
- optional source-cache and bridge references
- direct promotion dry-run records for validation

All inputs are repo-local JSON files. The runtime never performs observations, source access, network calls, model calls, downloads, uploads, or account operations.

## Readiness

Readiness values include:

- `ready_for_future_reviewed_record_proposal`
- `not_ready_missing_evidence`
- `not_ready_missing_review`
- `not_ready_policy_blocked`
- `not_ready_rights_blocked`
- `not_ready_risk_blocked`
- `not_ready_conflict_unresolved`
- `not_ready_duplicate_uncertain`
- `not_ready_identity_uncertain`
- `not_ready_source_uncertain`
- `not_ready_representation_uncertain`
- `not_evaluable`

Readiness is only a dry-run conclusion. It never allows public-index or master-index mutation.

## Blockers

Blocker categories cover missing evidence, missing review, source/provenance gaps, unresolved conflict, duplicate uncertainty, identity or representation uncertainty, rights/risk/policy/privacy blocks, review decision gaps, and not-evaluable cases. Blockers are preserved in reports and are not automatically resolved, merged, or deleted.

## Outputs

Allowed outputs are promotion dry-run records, summaries, blocker reports, future review items, future WorkUnit seeds, and future reviewed-record proposal placeholders. Forbidden outputs include candidate acceptance, evidence truth, public records, public-index mutation, master-index mutation, rights clearance, malware safety, verified installability, exhaustive-search proof, and production-readiness claims.

## Validation

Use:

```bash
python scripts/validate_candidate_promotion_dry_run.py
python scripts/run_candidate_promotion_dry_run.py --candidate examples/candidates/search_need_candidate_v0.json --review examples/review_queue_entries/candidate_needs_review_v0.json --check
```
