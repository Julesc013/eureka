# OBS0-02 Execution Readiness

Batch 0 is ready for human execution.

- Pending slots: 39
- Observed slots created by OBS0-02: 0
- Execution manifest: `control/inventory/observations/manual_observation_batch_0_slot_manifest.json`
- Audit manifest: `control/audits/obs0-02-manual-observation-batch-0-execution-packet-v0/slot_execution_manifest.json`

Prepare or inspect the current slot state:

```powershell
python scripts/prepare_manual_observation_batch0_execution.py --check
```

Validate the execution packet:

```powershell
python scripts/validate_manual_observation_batch0_execution.py
```

Human next step: pick one pending slot, perform the external search manually, record the required fields, and validate the completed observation.

Still forbidden: browser automation, browser opening by scripts, scraping, crawling, external API calls, model/provider calls, fabricated results, observed-file creation by preparation tasks, and marking pending slots observed without an actual human observation.
