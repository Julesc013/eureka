# Reviewed Public Index Rebuild Readiness

Current runtime status: contract only.

## Ready

- Contract shape for future reviewed public-index rebuild inputs.
- Contract shape for future reviewed public record proposals.
- Review, input, output, path, record, and truth policies.
- Public-safe examples and validator coverage.

## Still Forbidden

- Public-index rebuild runtime.
- Public-index mutation.
- Master-index mutation.
- Candidate or evidence acceptance.
- Current public truth creation.
- `site/dist/` or `site/dist/data/public_index/` mutation.
- Live source access, provider calls, uploads, downloads, accounts, telemetry, and local private state creation.

## Before Actual Rebuild Runtime

A later task must add explicit operator approval, reviewed proposal selection, public index output path policy, rollback/audit requirements, and public search behavior review.

## Before Public Or Master Index Mutation

The repository needs a separate reviewed runtime task with evidence-backed records, human approval, conflict and duplicate review, rights/risk review, and architecture boundary approval.

## Recommended Next Task

TRACK-B-21 - Pack builder runtime.
