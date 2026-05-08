# TRACK-B-02 Validation

## Required Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/nodes/node_policy_registry.json`
- `python -m json.tool control/inventory/nodes/node_action_policy.json`
- `python -m json.tool control/inventory/nodes/node_source_access_policy.json`
- `python -m json.tool control/inventory/nodes/node_output_policy.json`
- `python -m json.tool control/inventory/nodes/node_review_gate_policy.json`
- `python -m json.tool control/audits/track-b-02-node-policy-contract-v0/track_b_02_report.json`
- `python scripts/validate_eureka_node_manifest.py`
- `python scripts/validate_eureka_node_policy.py`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/validate_track_a_contracts.py`
- `python scripts/validate_agent_assisted_observation_policy.py`
- `python scripts/validate_observation_candidate.py`

## AIDE Lite Commands

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval list`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py adapter validate`

## Current Result

- PASS: `git status --short` showed only TRACK-B-02 scoped changes before commit.
- PASS: `git diff --check`.
- PASS: all required `python -m json.tool` checks.
- PASS: `python scripts/validate_eureka_node_manifest.py`.
- PASS: `python scripts/validate_eureka_node_policy.py`.
- PASS: `python -m unittest discover -s tests -t .` ran 1864 tests.
- PASS: `python scripts/check_architecture_boundaries.py`.
- PASS: `python scripts/validate_track_a_contracts.py`.
- PASS: `python scripts/validate_agent_assisted_observation_policy.py`.
- PASS: `python scripts/validate_observation_candidate.py`.
- PASS: AIDE Lite `pack`, `doctor`, `test`, `selftest`, `eval list`, `eval run`, and `adapter validate`.
- WARN: AIDE Lite `validate` reported review-packet path warnings only.
- WARN: AIDE Lite `verify` reported 15 warnings and 0 errors; warnings were review-packet missing path references and active-task diff-scope bookkeeping for new Track B paths.
- WARN: AIDE Lite `review-pack` completed and carried the WARN verifier result.
