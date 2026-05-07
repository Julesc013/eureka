# OBS0-02 Validation

Required validation:

```powershell
git status --short
git diff --check
python -m json.tool control/inventory/observations/manual_observation_batch_0_execution.json
python -m json.tool control/inventory/observations/manual_observation_batch_0_slot_manifest.json
python -m json.tool control/audits/obs0-02-manual-observation-batch-0-execution-packet-v0/obs0_02_report.json
python scripts/validate_manual_observation_protocol.py
python scripts/prepare_manual_observation_batch0_execution.py --check
python scripts/validate_manual_observation_batch0_execution.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
python scripts/validate_track_a_contracts.py
```

OBS0-02 validation is local only. It must not open browsers, fetch URLs, scrape, crawl, call APIs, call models/providers, create observed files, or mark pending slots observed.

## Latest Run

- PASS: `python -m json.tool control/inventory/observations/manual_observation_batch_0_execution.json`
- PASS: `python -m json.tool control/inventory/observations/manual_observation_batch_0_slot_manifest.json`
- PASS: `python -m json.tool control/audits/obs0-02-manual-observation-batch-0-execution-packet-v0/obs0_02_report.json`
- PASS: `python scripts/validate_manual_observation_protocol.py`
- PASS: `python scripts/prepare_manual_observation_batch0_execution.py --check`
- PASS: `python scripts/validate_manual_observation_batch0_execution.py`
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
- PASS: `py -3 .aide/scripts/aide_lite.py adapter validate`
- WARN: `py -3 .aide/scripts/aide_lite.py verify` reported stale reference and diff-scope warnings; errors were zero.
- WARN: `py -3 .aide/scripts/aide_lite.py review-pack` inherited the verifier WARN result; budget passed.
