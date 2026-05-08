# OBS Candidate To SearchNeed Seeds

## Purpose

OBS-AGENT-04 adds a repo-local, review-gated conversion layer from
ObservationCandidate records and observation candidate review queue entries into
SearchNeed seed drafts.

A SearchNeed seed is a draft input for future planning. It is not a runtime SearchNeed,
not an observed baseline, not accepted evidence, not source
approval, and not public truth. The layer exists so local candidate work can be
triaged before Track B defines and accepts runtime SearchNeed semantics.

## Allowed Inputs

The conversion layer may read committed repo-local material only:

- `control/inventory/observations/observation_candidate_review_queue.json`
- OBS-AGENT-01, OBS-AGENT-02, and OBS-AGENT-03 audit artifacts
- `examples/observation_candidates/**`
- `examples/observation_reviews/**`
- `contracts/query/**`
- `docs/operations/**`
- `evals/search_usefulness/**` when already committed

The scripts do not read private caches, secrets, browser state, live source
results, downloaded archives, or untracked external data.

## Outputs

OBS-AGENT-04 produces:

- SearchNeed seed contracts under `contracts/query/`
- SearchNeed seed and conversion examples under `examples/`
- A conversion policy, priority model, and seed manifest under
  `control/inventory/observations/`
- Build, validation, and summarization scripts under `scripts/`
- An audit packet under
  `control/audits/obs-agent-04-candidate-to-search-need-seeds-v0/`

These outputs are governance artifacts. They are review materials, not product
runtime state.

## Candidate Conversion Boundary

ObservationCandidates can suggest SearchNeed seed drafts when the review queue
has enough local structure to describe a user action. That conversion is only a
proposal. The draft preserves limitations, source policy posture, missing
evidence, and downstream Track B dependencies.

The conversion layer must not:

- Approve or reject ObservationCandidates.
- Create accepted SearchNeed runtime records.
- Convert source gaps into source approval.
- Convert local eval gaps into object truth.
- Convert demand signal into evidence truth.
- Mark pending observation slots as observed.
- Mutate a master index.

## Human Review

Human review is required before downstream use. A reviewer may later tune,
defer, reject, mark duplicate, request more evidence, or approve a seed for a
future Track B process. That future approval still does not create observed
baseline evidence, accepted evidence truth, source access, or runtime state by
itself.

## Track B Dependency

Track B can continue in parallel because OBS-AGENT-04 does not modify Track B
runtime behavior. The seed contracts are query/governance contracts for draft
records. Track B must separately define runtime SearchNeed semantics before any
seed can be accepted as runtime state.

## No Live External Searches

The build and validation scripts use committed repo-local inputs only. They do
not open browsers, call APIs, query search engines, scrape forums, query Reddit,
query Internet Archive, fetch live pages, call providers, or run model calls.

## Validation

Run:

```powershell
python scripts/build_search_need_seed_candidates.py --list-inputs
python scripts/build_search_need_seed_candidates.py --check
python scripts/validate_search_need_seed_candidates.py
python scripts/summarize_search_need_seed_candidates.py
```

Then run the broader repository checks requested by the active task packet.

## No Goals

- No external observation.
- No accepted evidence.
- No observed baseline.
- No accepted runtime SearchNeed.
- No source approval.
- No source sync, connector, probe, download, upload, account, or telemetry.
- No product behavior change.
- No master-index mutation.
