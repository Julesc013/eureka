# Policy And Safety Report

## Controls Added

- fallback enabled/disabled switch
- source family allowlist
- source family disabled list
- per-run request budget
- candidate limit
- timeout budget guard

## Truth Boundary

Fallback summaries, source observations, candidates, and needs all carry:

- `accepted_truth: false`
- `verified: false`
- `reviewed_record_created: false`
- `reviewed_index_mutated: false`
- `master_index_mutated: false`
- `public_index_mutated: false`

Promotion remains deferred to `REVIEW-LEDGER-00`.

## Source Scope

The first slice is metadata-candidate shaped. It does not add:

- downloads
- file fetching
- crawling
- Wayback replay
- raw response commits
- upload/extraction/execution behavior

## Public Surface

Resolution-run public projection is passive. It exposes allowed public actions only as:

- `view`
- `inspect_evidence`

Focused tests assert that fallback projection does not expose `review_candidate`, `promote`, `reject`, or `rebuild_index`.
