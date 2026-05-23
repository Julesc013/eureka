# OBS Candidate To WorkUnit Seeds

## Purpose

OBS-AGENT-05 adds a repo-local, review-gated conversion layer from
ObservationCandidate records, observation candidate review queue entries, and
SearchNeed seed drafts into WorkUnit seed drafts.

A WorkUnit seed is a bounded task proposal. It is not an executable WorkUnit,
not a runtime WorkUnit, not an observed baseline, not accepted evidence, not
source approval, and not public truth. The layer exists so OBS candidate work
can be shaped for later Track B planning without running work.

## Allowed Inputs

The conversion layer may read committed repo-local material only:

- `control/inventory/observations/observation_candidate_review_queue.json`
- `control/inventory/observations/search_need_seed_manifest.json`
- OBS-AGENT-01 through OBS-AGENT-04 audit artifacts
- `examples/observation_candidates/**`
- `examples/search/need_seeds/**`
- `contracts/query/**`
- read-only Track B WorkUnit contracts under `contracts/node/`
- `docs/operations/**`

The scripts do not read private caches, secrets, browser state, live source
results, downloaded archives, or untracked external data.

## Outputs

OBS-AGENT-05 produces:

- WorkUnit seed contracts under `contracts/query/`
- WorkUnit seed and conversion examples under `examples/`
- A conversion policy, priority model, and seed manifest under
  `control/inventory/observations/`
- Build, validation, and summarization scripts under `scripts/`
- An audit packet under
  `control/audits/obs-agent-05-candidate-to-workunit-seeds-v0/`

These outputs are governance artifacts. They are review materials, not product
runtime state.

## Conversion Boundary

ObservationCandidates can suggest bounded work, review queue entries can
prioritize it, and SearchNeed seeds can clarify the user action. The resulting
WorkUnit seed remains a proposal. It preserves limitations, source policy
posture, missing evidence, and downstream Track B dependencies.

The conversion layer must not:

- Approve or reject ObservationCandidates.
- Create accepted WorkUnit runtime records.
- Execute WorkUnits.
- Convert source gaps into source approval.
- Convert local eval gaps into object truth.
- Mark pending observation slots as observed.
- Mutate a master index.

## Human Review

Human review is required before downstream use. A reviewer may later tune,
defer, reject, mark duplicate, request more evidence, or approve a seed for a
future Track B process. That future approval still does not execute work,
create observed baseline evidence, accept evidence truth, grant source access,
or create runtime state by itself.

## Track B Dependency

Track B can continue in parallel because OBS-AGENT-05 does not modify Track B
runtime behavior. Track B must separately define executable WorkUnit semantics,
node capabilities, local state handling, idempotency, recovery, and result
contracts before any seed can become executable work.

## No Live External Work

The build and validation scripts use committed repo-local inputs only. They do
not open browsers, call APIs, query search engines, scrape forums, query Reddit,
query Internet Archive, fetch live pages, call providers, run model calls,
download files, upload files, or execute WorkUnits.

## Validation

Run:

```powershell
python scripts/build_workunit_seed_candidates.py --list-inputs
python scripts/build_workunit_seed_candidates.py --check
python scripts/validate_workunit_seed_candidates.py
python scripts/summarize_workunit_seed_candidates.py
```

Then run the broader repository checks requested by the active task packet.

## No Goals

- No external observation.
- No WorkUnit execution.
- No accepted runtime WorkUnit.
- No accepted evidence.
- No observed baseline.
- No source approval.
- No source sync, connector, probe, download, upload, account, or telemetry.
- No product behavior change.
- No master-index mutation.
