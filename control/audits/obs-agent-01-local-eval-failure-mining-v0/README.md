# OBS-AGENT-01 Local Eval Failure Mining

## What Was Added

- OBS-local eval failure mining policy.
- Candidate batch manifest for five review-gated candidates.
- Compact ObservationCandidate examples for batch, source, extraction, ranking, and policy-blocked cases.
- Local-only mining and validation scripts.
- Operation tests for deterministic output and boundary protection.

## OBS Side Lane Boundary

This audit runs in the Observation side lane. It prepares local candidate evidence only and does not duplicate Track B runtime, node, WorkUnit, contract, local-state, source-access, or product behavior work.

## No Live External Observations

No browsers were opened. No external searches, API calls, scraping, crawling, downloads, model/provider calls, live source probes, or source connectors were used. Inputs are committed repo-local files only.

## Review Gate

Every candidate remains proposed or policy-blocked and requires human review. Candidates are not observed baselines, accepted evidence, source validation, or index mutations.

## Parallel Track B

Local preflight observed Track B work through TRACK-B-06. Queue and task-packet updates were intentionally deferred because the latest local AIDE packet points at Track B state and a separate Track B machine may be active.

## Validation Commands

```text
python scripts/mine_local_eval_observation_candidates.py --list-inputs
python scripts/mine_local_eval_observation_candidates.py --check
python scripts/validate_obs_agent_local_eval_mining.py
python scripts/validate_observation_candidate.py
python scripts/summarize_observation_candidates.py
python -m unittest tests.operations.test_obs_agent_local_eval_mining
```

Broader validation results are recorded in `validation.md`.

## No-Goals

- No external observation.
- No accepted evidence.
- No pending manual slot completion.
- No product runtime or public route change.
- No Track B implementation.
- No hosting, live probe, source sync, connector, download, upload, account, telemetry, native, rights-clearance, malware-safety, installability, or global-search claim.

## Next Task

OBS-AGENT-02 - Source gap candidate generation.
