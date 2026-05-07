# Batch 0 Observation Protocol

Batch 0 uses the canonical manual observation protocol:

- `docs/operations/MANUAL_OBSERVATION_PROTOCOL.md`
- `docs/operations/MANUAL_OBSERVATION_ANTI_FABRICATION_CHECKLIST.md`
- `docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md`

## Batch Scope

Batch 0 contains pending slots only. This file adds procedure, not observations.

## Procedure

1. Pick one pending slot from `observations/pending_batch_0_observations.json`.
2. Manually search the named external system.
3. Record only visible, manually observed facts.
4. Preserve rank, title, locator, short snippet or summary, usefulness, limitations, Eureka-equivalence note, and failure class.
5. Validate the completed observation before committing it.

## Forbidden

No browser automation, scraping, crawling, URL fetching, external APIs, model/provider calls, fabricated results, or pending-to-observed status changes without manual evidence.
