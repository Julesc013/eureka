# Observation Validator Status

Status classification: `complete`

Validator script:

- `scripts/validate_external_baseline_observations.py`

Related local helpers:

- `scripts/report_external_baseline_status.py`
- `scripts/list_external_baseline_observations.py`
- `scripts/create_external_baseline_observation.py`
- `scripts/run_external_baseline_comparison.py`
- `scripts/validate_external_baseline_comparison_report.py`

Validator command:

```powershell
python scripts/validate_external_baseline_observations.py --json
```

Current result:

- Status: `valid`
- Errors: none
- Batch 0 records: 39 pending, 0 observed

Capabilities:

- Verifies systems are manual-only.
- Verifies the observation schema enum and score ranges.
- Verifies pending manifests and Batch 0 selected query/system slots.
- Rejects observed records with placeholders, missing manual metadata, missing top results, or incomplete scores.
- Rejects prohibited automated collection labels such as scraping, API use, or crawling.

Repair guidance:

- Keep pending records pending until a human enters real observations.
- For observed records, replace placeholders, set `collection_method` to `manual` or `manual_entry`, include required metadata, include bounded top results, and complete all usefulness scores.
- Run the validator before attempting comparison.

