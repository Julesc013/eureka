# Observation Candidate Review Queue

The observation candidate review queue is an OBS side-lane governance artifact. It gathers repo-local ObservationCandidate records into a deterministic list for later human review.

The queue is not approval. It is not rejection. It is not an observed baseline, accepted evidence, source policy approval, SearchNeed record, WorkUnit record, connector runtime, or master-index mutation.

## How Candidates Enter

Candidates enter the queue from committed repo-local materials:

- ObservationCandidate examples under `examples/observation_candidates/`.
- OBS-AGENT-01 local eval candidate manifests.
- OBS-AGENT-02 source gap candidate manifests.

The queue builder deduplicates by `observation_candidate_id`, keeps candidate file references, applies deterministic advisory triage, and emits recommended future review actions.

## Queue Output

Each queue entry records:

- candidate identity and candidate file path
- candidate type, status, origin, source family, and source access mode
- proposed review state
- recommended future review action
- priority score and band
- review boundary booleans

Every entry must keep:

- `review_required: true`
- `accepted_as_observed_baseline: false`
- `accepted_as_evidence_truth: false`
- `master_index_mutation_allowed: false`

## Human Review Decisions

A human can later approve, reject, defer, mark duplicate, mark policy-blocked, or request more evidence using the governed review decision contract. OBS-AGENT-03 does not record those decisions.

Future recommended actions include source lead review, WorkUnit seed review, SearchNeed seed review, manual observation review, policy block review, duplicate review, defer, reject, and request more evidence.

All recommendations remain future/deferred. A recommendation does not change candidate status and does not authorize downstream work.

## Track B Boundary

Track B may consume queue items only after matching contracts and review gates exist. Candidate-to-SearchNeed and candidate-to-WorkUnit conversion remain future tasks. This queue can run in parallel with Track B because it does not change Track B runtime, contracts beyond the review-queue contract, public routes, source sync, or product behavior.

## Source Policy Boundary

Approving a source lead later would not itself approve live source access. Source access still requires a separate source policy decision with scope, allowed and forbidden surfaces, terms and robots posture, privacy posture, rights risk posture, rate limits, timeout, cache/evidence destination, and kill switch.

## Validation

```powershell
python scripts/build_observation_candidate_review_queue.py --list-inputs
python scripts/build_observation_candidate_review_queue.py --check
python scripts/validate_observation_candidate_review_queue.py
python scripts/summarize_observation_candidate_review_queue.py
python -m unittest tests.contracts.test_observation_candidate_review_queue_contract
python -m unittest tests.operations.test_observation_candidate_review_queue
```

## No-Goals

- No actual external observations.
- No browser automation or browser opening.
- No external search automation.
- No scraping, crawling, API calls, downloads, installs, uploads, accounts, telemetry, model calls, or provider calls.
- No accepted observation candidates.
- No accepted evidence truth.
- No observed baseline creation.
- No source approval or source sync runtime.
- No SearchNeed or WorkUnit record creation.
- No public route activation, hosted backend claim, product behavior change, or Track B duplicate implementation.
- No master-index mutation.
