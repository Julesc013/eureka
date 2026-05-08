# TRACK-B-01 Validation

## Required Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/nodes/eureka_node_manifest_policy.json`
- `python -m json.tool control/inventory/nodes/node_mode_registry.json`
- `python -m json.tool control/inventory/nodes/node_capability_registry.json`
- `python -m json.tool control/audits/track-b-01-eureka-node-manifest-v0/track_b_01_report.json`
- `python scripts/validate_eureka_node_manifest.py`
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

- PASS: `git status --short` showed only TRACK-B-01 scoped changes before commit.
- PASS: `git diff --check`.
- PASS: all required `python -m json.tool` checks.
- PASS: `python scripts/validate_eureka_node_manifest.py`.
- PASS: `python -m unittest discover -s tests -t .` ran 1845 tests.
- PASS: `python scripts/check_architecture_boundaries.py`.
- PASS: `python scripts/validate_track_a_contracts.py`.
- PASS: `python scripts/validate_agent_assisted_observation_policy.py`.
- PASS: `python scripts/validate_observation_candidate.py`.
- WARN: `py -3 .aide/scripts/aide_lite.py validate` reported review-packet path warnings only.
- WARN: `py -3 .aide/scripts/aide_lite.py verify` reported 10 warnings and 0 errors; warnings were review-packet missing path references and active-task diff-scope bookkeeping.
- WARN: `py -3 .aide/scripts/aide_lite.py review-pack` completed and carried the WARN verifier result.
- PASS: remaining AIDE Lite commands: `pack`, `doctor`, `test`, `selftest`, `eval list`, `eval run`, and `adapter validate`.
