# Manual Observation Protocol

Manual observation is human-operated evidence collection for external baseline comparison. It is not automated scraping, live probing, source sync, or search-engine automation.

## Purpose

Manual observations give Eureka reviewable external-baseline evidence for later SearchNeed, Candidate, Absence, Compare, and WorkUnit fixtures. A pending slot is not an observed baseline. A guessed result is not evidence.

## Scope

This protocol applies to Manual Observation Batch 0 under `evals/search_usefulness/external_baselines/batches/batch_0/` and to future manual observation batches unless a newer protocol supersedes it.

## Observer Responsibilities

- Use the query and external system named by the pending slot.
- Record only what was actually visible during the manual session.
- Keep the result public-safe and reviewable.
- Preserve uncertainty, missing results, near matches, stale pages, and limitations.
- Leave incomplete slots as `pending_manual_observation`.

## Required Fields

Observed-result records should include:

- date/time of observation
- observer-entered system name
- query string submitted
- result rank or position
- title
- URL or stable source locator
- snippet or short public-safe summary
- usefulness note
- observed limitations
- whether Eureka has equivalent evidence
- failure class: source, capability, ranking, extraction, compatibility, representation, identity, temporal, policy, or not evaluable

No-result records should include the same session fields plus searched scope, visible result count if known, no-result explanation, limitations, and failure class.

Pending records must keep observation fields empty or null and must not contain top results.

## Allowed Manual Steps

- Open the named external system manually in a human-operated browser or documented manual tool.
- Enter the query exactly or record the exact query variation used.
- Record visible result titles, ranks, locators, and short snippets or summaries.
- Record near matches and why they do or do not satisfy the need.
- Record source, capability, ranking, extraction, compatibility, representation, policy, or identity gaps.

## Forbidden Automated Steps

- No browser automation.
- No automated external search.
- No scraping or crawling.
- No URL fetching by script.
- No external API calls.
- No model/provider calls.
- No model-generated search summaries as observations.
- No source connector or live probe runtime.

## Recording Top Results

Record the top visible results in order. For each result, include rank, title, URL or stable locator, short snippet or public-safe summary, usefulness note, observed limitations, Eureka equivalent evidence status, and failure classes.

If the result is useful, explain why. If it is not useful, explain the mismatch rather than deleting it.

## No-Result Cases

If the manual session produces no visible result, record `observation_kind: no_result`, visible result count if known, searched scope, any filters, limitations, and a failure class such as `external_baseline_unavailable`, `source_gap`, `capability_gap`, or `not_evaluable`.

Do not convert no result into exhaustive global absence.

## Near Matches

Record near matches with their rank and locator when visible. Mark them as `near_match_only` when they are related but do not satisfy the query need.

## Uncertain Observations

If identity, compatibility, source authority, or result usefulness is uncertain, record the uncertainty directly. Do not choose a winner by inference.

## Snippets And Copyright

Use short public-safe snippets or summaries. Do not copy long excerpts. Prefer paraphrase when the visible text is lengthy or copyright-sensitive.

## Privacy

Do not record account names, private paths, cookies, personal data, raw browser profile state, local search history, or private user data.

## Dynamic Or Stale Pages

Record date/time, system name, query, filters, and limitations. If results appear personalized, unstable, blocked, or stale, mark that as a limitation.

## Pending Vs Observed

Use `pending_manual_observation` until a human completes a manual session and fills required fields. Never mark a slot observed from memory, expectation, model output, or prior unstored browsing.

## Validation

Run:

```powershell
python scripts/validate_manual_observation_protocol.py
python scripts/validate_external_baseline_observations.py
```

The validator is local-only. It does not browse, fetch URLs, call APIs, or perform observations.
