# Manual Observation Slot Completion Guide

Use this checklist for one Batch 0 slot at a time.

## Checklist

1. Identify the slot ID from the Batch 0 pending file.
2. Confirm the system/query pair before opening anything manually.
3. Manually open and search the external system.
4. Record the observation timestamp from the manual session.
5. Record the exact query submitted and any filters or scope.
6. Record result rank, title, URL or stable locator, and a short public-safe snippet or summary.
7. Record usefulness assessment and first useful result rank if one exists.
8. Record failure taxonomy classes from `docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md`.
9. Record Eureka comparison fields if comparable evidence is available.
10. Record limitations, uncertainty, staleness, and any privacy/copyright constraints.
11. Validate the completed file locally.
12. Leave the slot pending if the manual observation was not actually completed.

Do not mark observed unless the human observation was actually performed.

## Required Human Fields

- `operator`
- `observed_at`
- `browser_or_tool`
- `exact_query_submitted`
- `filters_or_scope`
- `top_results` or a no-result summary
- `first_useful_result_rank`
- `usefulness_scores`
- `failure_modes`
- `evidence_limitations`
- `staleness_notes`

## Anti-Fabrication Reminders

- Do not invent titles, URLs, snippets, ranks, or timestamps.
- Do not copy from memory or model-generated summaries.
- Do not classify a system as searched unless it was manually searched.
- Do not mark Eureka better or worse without comparable evidence.
- Do not use scraping, crawling, browser automation, external APIs, live probes, or source connectors.
