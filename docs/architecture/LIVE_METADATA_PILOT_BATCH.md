# LIVE-METADATA-PILOT-BATCH-00

The live metadata pilot is an approval-gated source observation lane over seed
queries. It turns curated frontier-media and legacy-software queries into
bounded Internet Archive metadata request plans, redacted metadata summaries,
review-only candidate records, SCOUT trails, review batch packets, and snapshot
handoffs.

It is not a crawler, public source fanout, download lane, extraction lane, or
production-readiness claim.

## Flow

1. Operator approval is checked.
2. Seed queries are selected from existing seed batches.
3. Query plans are reused from the query planner and seed batch runtimes.
4. Request plans are built for metadata-only Internet Archive search.
5. Dry-run and fixture modes produce deterministic, public-safe summaries.
6. Approved live mode is blocked unless a valid approval file exists.
7. Redacted summaries become review-only candidates.
8. SCOUT and review batch packets are produced as handoffs.

## Boundaries

- No raw live response commit.
- No downloads or extraction.
- No accepted truth.
- No reviewed, master, or public index mutation.
- No public mutation or public live source fanout.
- No deployment or launch claim.
