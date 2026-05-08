# OBS-REPLAN-01 Validation

Required validation:

```powershell
git status --short
git diff --check
python -m json.tool control/inventory/observations/agent_assisted_observation_policy.json
python -m json.tool control/inventory/observations/observation_candidate_review_policy.json
python -m json.tool control/inventory/observations/obs_parallel_development_policy.json
python -m json.tool control/inventory/observations/observation_source_access_modes.json
python -m json.tool control/audits/obs-replan-01-agent-assisted-observation-workflow-v0/obs_replan_01_report.json
python scripts/validate_agent_assisted_observation_policy.py
python scripts/validate_observation_candidate.py
python scripts/summarize_observation_candidates.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
python scripts/validate_track_a_contracts.py
```

OBS-REPLAN-01 validation is local only. It must not open browsers, fetch URLs, scrape, crawl, call APIs, call models/providers, create observed files, accept observation candidates as truth, or mutate the master index.

## Latest Run

- PASS: `python -m json.tool control/inventory/observations/agent_assisted_observation_policy.json`
- PASS: `python -m json.tool control/inventory/observations/observation_candidate_review_policy.json`
- PASS: `python -m json.tool control/inventory/observations/obs_parallel_development_policy.json`
- PASS: `python -m json.tool control/inventory/observations/observation_source_access_modes.json`
- PASS: `python -m json.tool control/audits/obs-replan-01-agent-assisted-observation-workflow-v0/obs_replan_01_report.json`
- PASS: `python scripts/validate_agent_assisted_observation_policy.py`
- PASS: `python scripts/validate_observation_candidate.py`
- PASS: `python scripts/summarize_observation_candidates.py`
- PASS: `python scripts/validate_manual_observation_protocol.py`
- PASS: `python scripts/validate_manual_observation_batch0_execution.py`
- PASS: `python scripts/validate_track_a_contracts.py`
- PASS: `python -m unittest discover -s tests -t .`
- PASS: `python scripts/check_architecture_boundaries.py`
- PASS: `py -3 .aide/scripts/aide_lite.py doctor`
- PASS: `py -3 .aide/scripts/aide_lite.py validate`
- PASS: `py -3 .aide/scripts/aide_lite.py test`
- PASS: `py -3 .aide/scripts/aide_lite.py selftest`
- PASS: `py -3 .aide/scripts/aide_lite.py eval list`
- PASS: `py -3 .aide/scripts/aide_lite.py eval run`
- PASS: `py -3 .aide/scripts/aide_lite.py adapter validate`
- WARN: `py -3 .aide/scripts/aide_lite.py verify` reported stale-reference and diff-scope warnings; errors were zero.
- WARN: `py -3 .aide/scripts/aide_lite.py review-pack` inherited the verifier WARN result; budget passed.
