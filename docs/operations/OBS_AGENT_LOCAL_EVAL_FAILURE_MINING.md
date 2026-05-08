# OBS Agent Local Eval Failure Mining

OBS-AGENT-01 mines committed repo-local materials for likely observation gaps. It prepares review-gated ObservationCandidate records from local evals, hard-query packs, observation manifests, static demo summaries, and governance reports. It does not run live searches or produce observed external baseline evidence.

## Purpose

The goal is to convert existing local signals into a small set of reviewable candidates:

- Local eval failure candidates for query classes that the repo already labels as weak.
- Source gap candidates for missing source coverage.
- Extraction or member-level candidates for package, media, OCR, or archive-member needs.
- Ranking candidates for local search or usefulness weaknesses.
- Policy-blocked candidates where a useful external path cannot be accessed by agents without a source policy.

These candidates help humans approve, reject, tune, deduplicate, or defer follow-up work without confusing local planning evidence with observed truth.

## Allowed Inputs

The miner may inspect only committed repo-local paths allowed by `control/inventory/observations/obs_agent_local_eval_failure_mining_policy.json`, including:

- `evals/search_usefulness/**`
- `examples/**`
- `control/audits/**`
- `control/inventory/observations/**`
- `site/dist/data/**`
- `site/dist/demo/**`
- `docs/operations/**`
- `docs/reference/**`

Forbidden inputs include live web access, browser sessions, API calls, downloaded binary archives, private local caches, `.aide.local/**`, `secrets/**`, `.git/**`, and untracked external data.

## Outputs

OBS-AGENT-01 produces:

- A local mining policy under `control/inventory/observations/`.
- A candidate batch manifest under `control/inventory/observations/`.
- Compact ObservationCandidate examples under `examples/observation_candidates/`.
- A mining script that writes only when explicit output paths are provided.
- A validator and tests for the OBS-local lane.
- An audit pack under `control/audits/obs-agent-01-local-eval-failure-mining-v0/`.

Generated candidates are proposed records. They are not observed baselines, accepted evidence, source validation, or index mutations.

## Candidate Boundary

An ObservationCandidate captures a local signal and a proposed next review action. It must keep these booleans fixed:

- `required_human_review: true`
- `accepted_as_observed_baseline: false`
- `accepted_as_evidence_truth: false`
- `master_index_mutation_allowed: false`

The candidate may later become a SearchNeed seed, WorkUnit seed, source lead, or manual observation target only after human review and after matching Track B contracts exist.

## Human Review

Human review decides the next safe action. It may approve a candidate as a source lead, WorkUnit seed, search-need seed, or manual observation target. Review does not make a candidate true and does not complete pending manual observation slots.

## No Live External Searches

This lane intentionally avoids live searches because the policy and source-access approvals are not the same as human-observed external evidence. The miner does not open browsers, call APIs, scrape, crawl, query Google, query Internet Archive, query forums, query Reddit, download files, or call models/providers.

## Parallel Track B Boundary

Track B can continue in parallel because this lane writes OBS-local policy, examples, scripts, tests, and audit evidence only. It reads Track B state only as branch context and does not mutate Track B contracts, runtime, public routes, source connectors, node runtime, WorkUnit runtime, local state runtime, or product behavior.

## Validation Commands

Use the local checks:

```text
python scripts/mine_local_eval_observation_candidates.py --list-inputs
python scripts/mine_local_eval_observation_candidates.py --check
python scripts/validate_obs_agent_local_eval_mining.py
python scripts/validate_observation_candidate.py
python scripts/summarize_observation_candidates.py
python -m unittest tests.operations.test_obs_agent_local_eval_mining
```

Broader repo validation may also run `python -m unittest discover -s tests -t .` and `python scripts/check_architecture_boundaries.py`.

## No-Goals

- No external observations.
- No browser automation or browser opening.
- No external search automation.
- No scraping, crawling, API calls, network calls, model calls, or provider calls.
- No observed result files.
- No accepted evidence.
- No pending slot completion.
- No index mutation.
- No public route, hosting, connector, source sync, download, upload, account, telemetry, native, or runtime behavior changes.
- No Track B implementation or duplicate Track B contract work.
