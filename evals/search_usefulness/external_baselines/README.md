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
- `batches/batch_0/` defines the first prioritized 13-query manual observation
  batch across the same three systems, with 39 pending slots and no observed
  top results.
- `instructions/` contains human operator instructions for each baseline.
- `reports/` is reserved for future committed comparison reports after manual
  observations exist.

## Entry Helpers

Manual Observation Entry Helper v0 adds stdlib-only local helper scripts:

- `scripts/list_external_baseline_observations.py` lists pending or observed
  slots, with filters for batch, query id, system id, and status.
- `scripts/create_external_baseline_observation.py` creates one fillable
  pending JSON file from a Batch 0 slot or prints it with `--stdout`.
- `scripts/validate_external_baseline_observations.py --file <path>`
  validates one human-edited observation file before commit.
- `scripts/report_external_baseline_status.py --batch batch_0 --next-pending`
  summarizes Batch 0 progress and the next pending slots.

These helpers do not perform observations, open browsers, fetch URLs, call
external APIs, scrape search systems, or mark records observed. A generated
file remains `pending_manual_observation` until a human adds the required
operator, timestamp, exact query, manually recorded top results, bounded scores,
limitations, and staleness notes.

## Report Shape

Validator and report scripts emit JSON-compatible summaries with:

- `status`
- `systems`
- `observations`
- `status_counts_by_system`
- `query_coverage`
- `batches`
- `errors`

External observations are time-sensitive and local to the operator, browser,
date, query wording, and visible UI state. They must not be treated as stable
global truth or as proof that Eureka beats Google or Internet Archive.

Manual Observation Batch 0 is implemented as preparation only. It selects a
manageable old-platform/member-discovery set for later human operation, but it
does not perform external observations, does not scrape or automate Google or
Internet Archive, and does not turn any pending slot into observed evidence.

Manual Observation Entry Helper v0 is implemented as local helper tooling only.
It improves the human entry workflow without adding external querying,
scraping, browser automation, URL fetching, comparison scoring, or observed
baseline claims.
