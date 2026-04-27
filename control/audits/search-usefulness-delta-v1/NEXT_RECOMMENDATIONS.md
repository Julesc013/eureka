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

Third follow-up status: More Source Coverage Expansion v1 is implemented under
`control/audits/more-source-coverage-expansion-v1/`. Archive evals now report
`capability_gap=1` and `satisfied=5`; the four old-platform partials are
source/evidence-backed satisfied under the current hard checks. The next
recommended milestone is Article/Scan Fixture Pack v0 because
`article_inside_magazine_scan` remains the only archive hard capability gap.

Fourth follow-up status: Article/Scan Fixture Pack v0 is implemented under
`control/audits/article-scan-fixture-pack-v0/`. Archive evals now report
`satisfied=6`; the article hard task is backed by a tiny synthetic article
segment, parent issue lineage, page-range metadata, and OCR-like fixture text.
The next recommended milestone is Manual External Baseline Observation Pack v0
because external baselines remain pending/manual for all 64 queries.

Fifth follow-up status: Manual External Baseline Observation Pack v0 is
implemented under `evals/search_usefulness/external_baselines/`. It seeds 192
pending manual observation slots and adds validation/reporting without
recording observed baselines. The next recommended milestone is Manual
Observation Batch 0.

Sixth follow-up status: Manual Observation Batch 0 is implemented under
`evals/search_usefulness/external_baselines/batches/batch_0/`. It selects 13
existing high-value query IDs and creates 39 pending query/system slots across
Google web search, Internet Archive metadata search, and Internet Archive
full-text/OCR search. It records no observed baselines. The next recommended
milestone is Manual Observation Batch 0 Execution, which must be performed by a
human operator without scraping or automation.

Seventh follow-up status: Manual Observation Entry Helper v0 is implemented as
local stdlib tooling for listing slots, creating fillable pending observation
files, validating one file or all files, and reporting Batch 0 progress. It
does not perform observations, fetch URLs, open browsers, scrape, automate
external searches, populate top results, or mark records observed. The next
recommended milestone remains Manual Observation Batch 0 Execution by a human
operator.

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

Now implemented as a targeted fixture pack. It did not attempt broad source
coverage; it added only bounded Firefox XP, blue FTP-client XP, Windows 98
registry repair, and Windows 7 utility/app evidence needed by the remaining
old-platform hard partials.

### Article/Scan Fixture Pack v0

Now the best immediate follow-up. It would add bounded scan/page/OCR/article
fixture evidence for `article_inside_magazine_scan`, the only remaining archive
hard capability gap. It should remain fixture-only and must not scrape or call
live Internet Archive.

### Manual External Baseline Observation Pack v0

Implemented after Article/Scan Fixture Pack v0 as a manual-only protocol under
`evals/search_usefulness/external_baselines/`. It defines schema, systems,
templates, instructions, pending slots, and validation/report scripts without
recording observed external baselines.

### Manual Observation Batch 0

Now implemented as a pending-only preparation batch. It does not perform
external observations. The next comparison step should be Manual Observation
Batch 0 Execution, where a human records observed evidence for selected slots
using the governed protocol.

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
