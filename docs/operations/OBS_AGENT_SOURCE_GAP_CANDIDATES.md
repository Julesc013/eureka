# OBS Agent Source Gap Candidates

OBS-AGENT-02 generates review-gated source gap observation candidates from committed repo-local material. It ranks missing source leads that may later become source policy decision packets, SearchNeed seeds, WorkUnit seeds, approved-source planning tasks, or connector-pattern candidates after the matching contracts and review gates exist.

This lane does not perform observations. It does not approve source access. It does not create evidence truth.

## Allowed Inputs

The generator may inspect committed repo-local files under:

- `evals/search_usefulness/**`
- `control/audits/**`
- `control/inventory/observations/**`
- `control/inventory/sources/**`
- `contracts/source/registry/**`
- `contracts/query/**`
- `docs/reference/**`
- `docs/operations/**`
- `examples/**`
- `site/dist/data/**`
- `site/dist/demo/**`

These inputs are used to identify local gaps in source coverage, metadata shape, old-platform coverage, release/version discovery, package identity, manual-only community evidence, and blocked baseline access.

## Forbidden Inputs

OBS-AGENT-02 must not use live web pages, browser sessions, API calls, downloaded binary archives, private local caches, `.aide.local/**`, `secrets/**`, `.git/**`, or untracked external data.

The task must not run external searches, query Google, query Internet Archive, query forums, query Reddit, fetch live pages, scrape, crawl, download, install, upload, create accounts, enable telemetry, or call models/providers.

## Outputs

The lane writes source gap policy and inventory records:

- `control/inventory/observations/obs_agent_source_gap_candidate_policy.json`
- `control/inventory/observations/obs_agent_source_gap_priority_model.json`
- `control/inventory/observations/obs_agent_source_gap_candidate_manifest.json`

It writes compact ObservationCandidate examples under `examples/observation_candidates/` and an audit pack under `control/audits/obs-agent-02-source-gap-candidate-generation-v0/`.

The generator supports:

```powershell
python scripts/generate_source_gap_observation_candidates.py --list-inputs
python scripts/generate_source_gap_observation_candidates.py --check
python scripts/generate_source_gap_observation_candidates.py --json-output control/audits/obs-agent-02-source-gap-candidate-generation-v0/source_gap_candidate_manifest.json --markdown-output control/audits/obs-agent-02-source-gap-candidate-generation-v0/source_gap_candidate_summary.md
```

It writes no files unless explicit output paths are supplied.

## Candidate Boundary

A source gap candidate is not source approval. A source lead is not evidence truth. A source family recommendation is not permission to crawl, probe, download, or enable a connector. A ranked source gap is only a review item.

All generated candidates must remain:

- `required_human_review: true`
- `accepted_as_observed_baseline: false`
- `accepted_as_evidence_truth: false`
- `master_index_mutation_allowed: false`

Product-boundary booleans must remain false. Pending manual observation slots must remain pending.

## Human Review

Human or operator review decides whether a candidate should be approved as a source lead, converted into a future WorkUnit/SearchNeed seed, deferred, rejected, marked duplicate, or kept policy-blocked.

Review must separately decide the source policy scope before any future source access. That decision needs source family scope, allowed and forbidden endpoints or surfaces, terms and robots posture, privacy posture, rights risk posture, rate limits, timeout, cache and evidence destination, kill switch, and reviewed output contract.

## Later Track B Use

Track B may consume these records only after matching contracts exist. Possible later uses include:

- SearchNeed seeds for source coverage and query decomposition.
- WorkUnit seeds for source policy decision packets.
- Approved-source planning tasks.
- Connector-pattern candidates for metadata-only source families.

The first Internet Archive metadata connector pattern should be selected later only after policy review confirms a bounded metadata-only scope, cache-first outputs, evidence attribution, no payload retrieval, no public-query fanout, no source sync runtime without approval, and no master-index mutation.

## Parallel Track B

This OBS lane is limited to control, inventory, docs, examples, scripts, tests, and audit evidence. It does not modify Track B runtime or contracts. The AIDE latest task packet may lag behind Track B, so this lane records observed Track B state as audit context rather than rewriting queue state.

## Validation

Run:

```powershell
git diff --check
python -m json.tool control/inventory/observations/obs_agent_source_gap_candidate_policy.json
python -m json.tool control/inventory/observations/obs_agent_source_gap_candidate_manifest.json
python -m json.tool control/inventory/observations/obs_agent_source_gap_priority_model.json
python -m json.tool control/audits/obs-agent-02-source-gap-candidate-generation-v0/obs_agent_02_report.json
python scripts/validate_observation_candidate.py
python scripts/generate_source_gap_observation_candidates.py --list-inputs
python scripts/generate_source_gap_observation_candidates.py --check
python scripts/validate_source_gap_observation_candidates.py
python -m unittest tests.operations.test_source_gap_observation_candidates
```

Broader repo and AIDE validation should be reported honestly. Existing environment warnings are acceptable only when OBS-specific validators and tests pass and the warning is not caused by this lane.

## No-Goals

- No actual external observations.
- No browser automation or browser opening.
- No external search automation.
- No scraping or crawling.
- No API calls, network calls, model calls, or provider calls.
- No source approval.
- No source sync runtime, live probes, source connectors, downloads, uploads, accounts, or telemetry.
- No observed baselines, accepted evidence truth, public truth, or master-index mutation.
- No public route activation, hosted backend claim, deployment change, native project creation, rights-clearance claim, malware-safety claim, verified-installability claim, or exhaustive-search claim.
- No Track B duplicate implementation or runtime/contract mutation.
