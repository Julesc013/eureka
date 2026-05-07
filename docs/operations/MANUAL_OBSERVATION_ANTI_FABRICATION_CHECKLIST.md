# Manual Observation Anti-Fabrication Checklist

Use this checklist before committing any manual observation record.

## Hard Rules

- No invented titles.
- No invented URLs or locators.
- No invented snippets or summaries.
- No invented result ranks.
- No inferred observation timestamps.
- No copying from memory.
- No expected external result unless actually observed.
- No `observed` status without a completed manual session.
- No automated scraping or browser automation.
- No API calls.
- No model-generated search summaries as observations.
- No external system marked searched unless it was manually searched.
- No marking Eureka better or worse without comparable evidence.

## Evidence Minimum

An observed result needs a timestamp, system name, query, rank, title, locator, short snippet or summary, usefulness note, limitations, Eureka-equivalence note, and failure class.

An observed no-result session needs a timestamp, system name, query, searched scope, visible result count if known, no-result note, limitations, and failure class.

## Stop And Leave Pending

Leave the slot pending when:

- the observer did not run a manual session
- the result page cannot be reviewed safely
- required fields are missing
- only memory or model output is available
- the external system was blocked or unavailable and the block was not recorded

## Review Prompt

Before changing `pending_manual_observation` to `observed`, ask:

- Did I personally observe this in a manual session?
- Can another reviewer understand the locator, rank, snippet or summary, and limitation?
- Did I avoid automation, API calls, long excerpts, private data, and unsupported comparison claims?
