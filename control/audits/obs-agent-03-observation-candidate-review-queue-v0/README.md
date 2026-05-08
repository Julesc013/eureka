# OBS-AGENT-03 Observation Candidate Review Queue

This audit pack records the OBS side-lane review queue for repo-local ObservationCandidate records.

## Added

- Review queue contract under `contracts/query/`.
- Review queue policy and triage rules under `control/inventory/observations/`.
- Deterministic review queue inventory and audit queue.
- Queue examples under `examples/observation_reviews/`.
- Builder, validator, and summarizer scripts.
- Contract and operation tests.
- Human review packet and future review item summaries.

## OBS Lane Boundary

This side lane is governance. It differs from Track B by queueing candidates for later human review without implementing runtime behavior, source sync, source access, SearchNeed records, WorkUnit records, or product routes.

## Queue Build

The queue is built from committed repo-local ObservationCandidate examples and OBS-AGENT-01/02 manifests. The builder deduplicates by `observation_candidate_id`, applies deterministic advisory triage, and emits future-only recommended actions.

## Human Use

Humans may later approve, reject, defer, mark duplicate, mark policy-blocked, or request more evidence through the review decision process. This pack records no such decisions.

## Forbidden

No live source access, browser use, API calls, external search, scraping, crawling, downloads, installs, uploads, accounts, telemetry, observed baseline creation, accepted evidence truth, source policy approval, SearchNeed record creation, WorkUnit record creation, or master-index mutation occurred.

## Deferred

- Candidate-to-SearchNeed seed conversion.
- Candidate-to-WorkUnit seed conversion.
- Source policy decision packets.
- Manual observation execution.
- Any Track B consumption after matching contracts and review gates exist.

## Validation

```powershell
python scripts/build_observation_candidate_review_queue.py --list-inputs
python scripts/build_observation_candidate_review_queue.py --check
python scripts/validate_observation_candidate_review_queue.py
python scripts/summarize_observation_candidate_review_queue.py
python -m unittest tests.contracts.test_observation_candidate_review_queue_contract
python -m unittest tests.operations.test_observation_candidate_review_queue
```

## Next Task

Recommended next task: `OBS-AGENT-04 - Candidate-to-SearchNeed seed conversion`.
