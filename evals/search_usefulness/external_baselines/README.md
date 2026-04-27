# Manual External Baseline Observations

Manual External Baseline Observation Pack v0 defines a governed way to record
human observations for external search baselines without scraping, live API
calls, crawlers, or automated result collection.

This area is protocol and eval metadata only. It does not perform Google
searches, Internet Archive searches, API calls, crawling, source probing, or
retrieval behavior. Pending slots are not observations.

## Files

- `systems.json` defines manual-only baseline systems.
- `observation.schema.json` documents the observation record shape.
- `observation_template.json` is a fillable placeholder, not evidence.
- `observations/pending_observations.json` enumerates the current query IDs and
  required manual baseline systems with `pending_manual_observation` status.
- `instructions/` contains human operator instructions for each baseline.
- `reports/` is reserved for future committed comparison reports after manual
  observations exist.

## Report Shape

Validator and report scripts emit JSON-compatible summaries with:

- `status`
- `systems`
- `observations`
- `status_counts_by_system`
- `query_coverage`
- `errors`

External observations are time-sensitive and local to the operator, browser,
date, query wording, and visible UI state. They must not be treated as stable
global truth or as proof that Eureka beats Google or Internet Archive.
