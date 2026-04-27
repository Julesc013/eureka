# Next Recommendations

## Recommended Next Milestone

`Hard Eval Satisfaction Pack v0`

Follow-up status: implemented under
`control/audits/hard-eval-satisfaction-v0/`. The follow-up moved archive evals
to `capability_gap=1` and `partial=5` without weakening hard tasks. The next
recommended milestone after that follow-up is Old-Platform Result Refinement
Pack v0.

Second follow-up status: Old-Platform Result Refinement Pack v0 is implemented
under `control/audits/old-platform-result-refinement-v0/`. Archive evals now
report `capability_gap=1`, `partial=4`, and `satisfied=1`. The next
recommended milestone is More Source Coverage Expansion v1 because four
old-platform hard tasks remain partial due exact-release, identity,
direct-artifact, or lane/evidence limits.

## Why This Comes Next

Old-Platform Source Coverage Expansion v0 produced a meaningful local audit
movement:

- `partial`: 5 to 20
- `source_gap`: 41 to 28
- `capability_gap`: 11 to 9

It also moved archive-resolution hard tasks toward source-backed evaluation:

- `capability_gap`: 5 to 1
- `not_satisfied`: 1 to 5

That means the next bottleneck is no longer just missing source material for
the selected hard tasks. The system now finds candidates, but the hard expected
outcomes are not satisfied. The next slice should make the current source-backed
candidate path satisfy hard evals honestly or explain exactly why it cannot.

## Acceptance Criteria

- Keep hard eval task IDs and expected-result requirements intact.
- Do not weaken hard expected-result hints to make results look better.
- Make source-backed candidates align with hard expected outcomes where the
  current fixture corpus supports it.
- Preserve `not_satisfied` for cases that still lack exact evidence.
- Add regression tests for each hard task that moves.
- Keep external baselines pending/manual.

## Alternatives Considered

### Old-Platform Result Refinement Pack v0

Strong candidate. Some current partials need better result lanes, user-cost
ordering, and direct/member preference. This likely becomes part of Hard Eval
Satisfaction Pack v0 or follows immediately after it.

### Compatibility Evidence Expansion v0

Still useful because `compatibility_evidence_gap` remains 25. It is not first
because the hard eval runner already exposes source-backed candidates that need
exact satisfaction work.

### More Source Coverage Expansion v1

Still useful because `source_coverage_gap` remains 49 and `source_gap` remains
28. It is not first because another broad fixture pack would not resolve the
five hard tasks now stuck at `not_satisfied`.

### Manual External Baseline Observation Pack v0

Deferred. Internal usefulness is now better, but external baselines should stay
manual and can wait until hard eval behavior is sharper.

### Rust Query Planner Parity Candidate v0

Deferred. Python remains the oracle, and current usefulness behavior is still
moving quickly.

### Public Alpha Rehearsal Evidence v0

Deferred. Public-alpha safety is green, but usefulness still needs hard-eval
satisfaction before a stronger supervised demo rehearsal.

## Do Not Do Next

- live crawling
- Google scraping
- Internet Archive scraping
- broad live source federation
- fuzzy/vector retrieval
- LLM planning
- production hosting
- native apps
- broad Rust rewrite
- installer automation
- arbitrary local filesystem ingestion
