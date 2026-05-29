# Active Discovery Next Plan

Goal: make Eureka useful before public alpha by turning hard queries into
candidate-producing source actions and reviewable leads.

## Required Product Behavior

For a weak or zero-result query, Eureka should do this:

```text
search query
-> reviewed local results
-> candidate/source-cache results
-> if weak, start a bounded ResolutionRun
-> plan source actions
-> run fixture/mock/operator-approved metadata actions
-> create candidate records
-> show candidate lanes
-> create review items
```

## Archive.org-Wide Metadata Search Requirement

Public alpha must be able to search Archive.org beyond Eureka's local reviewed
index. The bounded interpretation is:

- use Internet Archive item metadata search APIs for item-level discovery
- support cursor-based deep paging through the Archive search surface where
  needed
- fetch per-item metadata from `/metadata/{identifier}` only after search
  candidates are selected
- cache/redact source summaries into source-cache and candidate records
- route all candidate truth through review queue promotion

This is not:

- a full mirror of Archive.org
- a guarantee that every changing Archive.org record is present locally
- arbitrary crawling or scraping
- file download, file fetch, extraction, install, or execution
- public-query fanout without budgets, rate limits, cache policy, and kill
  switch

No downloads are approved by this plan.

## Next Queue

1. `ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-00`
2. `QUERY-TO-SOURCE-ACTION-PLANNER-00`
3. `CANDIDATE-INDEX-RUNTIME-00`
4. `SOURCE-ACTION-LIVE-METADATA-PILOTS-00`
5. `SCOUT-RUNTIME-00`
6. `REVIEW-BATCH-00`
7. `SEED-BATCH-FRONTIER-MEDIA-00`
8. `SEED-BATCH-LEGACY-SOFTWARE-00`
9. `SNAPSHOT-REFRESH-00`
10. `PUBLIC-ALPHA-REASSESS-00`

Only after reassessment should the queue return to deployment dry-run and
public alpha launch.

## First Implementation Acceptance

`ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-00` should prove:

- local reviewed results still work
- zero/weak local results create source-action plans
- Archive.org metadata search can run under explicit operator policy
- live metadata output becomes candidate records, not reviewed truth
- candidates appear in Workbench/search lanes as provisional leads
- review queue can accept, reject, mark near-miss, or promote selected records
- snapshot refresh can publish accepted reviewed records read-only

## Safety Defaults

Keep these false unless a later reviewed task explicitly changes them:

- `downloads_enabled`
- `extraction_enabled`
- `uploads_enabled`
- `accounts_enabled`
- `telemetry_enabled`
- `automatic_reviewed_truth`
- `public_or_master_index_mutation_from_live_results`
- `production_readiness_claimed`
- `public_launch_readiness_claimed`
