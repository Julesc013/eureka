# Candidate Promotion Dry-Run Review

Promotion dry-run review is the human gate between provisional local records and a future reviewed-record proposal task.

Reviewers should check:

- candidate identity and canonical key
- evidence candidate presence and provenance
- review queue approval for local dry-run only
- conflict and duplicate markers
- rights, risk, policy, privacy, source, and representation blockers
- public-index and master-index mutation boundaries

## Ready Does Not Promote

`ready_for_future_reviewed_record_proposal` only means a future task may draft a reviewed-record proposal. It does not accept evidence, accept a candidate, write public files, clear rights, establish malware safety, verify installability, or mutate the master index.

## Blocked Outcomes

Blocked dry-runs should preserve their blockers. Conflicts are not resolved automatically. Duplicate uncertainty does not merge or delete records. Rights/risk/policy blocks require separate reviewed decisions.

## Commands

```bash
python scripts/run_candidate_promotion_dry_run.py --candidate examples/candidates/search_need_candidate_v0.json --review examples/review_queue_entries/candidate_needs_review_v0.json --check
python scripts/validate_candidate_promotion_dry_run.py
```

Committed dry-run evidence may be written only to task audit `generated/` directories or explicit temporary test directories.
