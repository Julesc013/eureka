# Manual Observation Records

This directory contains manual external baseline observation records and the
current pending observation manifest.

Do not commit scraped Google results, scraped Internet Archive results,
automated search output, live API output, or crawler output. Pending records are
not observations and must not be counted as observed baselines.

Run:

```bash
python scripts/validate_external_baseline_observations.py
python scripts/report_external_baseline_status.py
```
