# OBS0-01 Validation

Required validation:

```powershell
git status --short
git diff --check
python -m json.tool control/inventory/observations/manual_observation_policy.json
python -m json.tool control/inventory/observations/manual_observation_failure_taxonomy.json
python -m json.tool control/audits/obs0-01-manual-observation-protocol-v0/obs0_01_report.json
python scripts/validate_manual_observation_protocol.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
python scripts/validate_track_a_contracts.py
```

AIDE Lite checks are recorded in the final response. WARN-only AIDE notes are acceptable when errors are zero.

## Latest Run

- PASS: `python -m json.tool control/inventory/observations/manual_observation_policy.json`
- PASS: `python -m json.tool control/inventory/observations/manual_observation_failure_taxonomy.json`
- PASS: `python -m json.tool control/audits/obs0-01-manual-observation-protocol-v0/obs0_01_report.json`
- PASS: `python scripts/validate_manual_observation_protocol.py`
- PASS: `python scripts/validate_external_baseline_observations.py`
- PASS: `python scripts/validate_track_a_contracts.py`
- PASS: `python -m unittest discover -s tests -t .`
- PASS: `python scripts/check_architecture_boundaries.py`
- PASS: `py -3 .aide/scripts/aide_lite.py doctor`
- PASS: `py -3 .aide/scripts/aide_lite.py validate`
- PASS: `py -3 .aide/scripts/aide_lite.py test`
- PASS: `py -3 .aide/scripts/aide_lite.py selftest`
- PASS: `py -3 .aide/scripts/aide_lite.py eval list`
- PASS: `py -3 .aide/scripts/aide_lite.py eval run`
- PASS: `py -3 .aide/scripts/aide_lite.py review-pack`
- PASS: `py -3 .aide/scripts/aide_lite.py adapter validate`
- WARN: `py -3 .aide/scripts/aide_lite.py verify` reported stale compact-packet scope and optional missing AIDE reference warnings; errors were zero.
