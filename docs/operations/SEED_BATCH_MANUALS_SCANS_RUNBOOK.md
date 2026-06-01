# Manuals/Scans Seed Batch Runbook

Run the fixture lane:

```text
python scripts/eureka_seed_batch_manuals_scans.py --fixture --json
```

Refresh examples and evidence:

```text
python scripts/eureka_seed_batch_manuals_scans.py --fixture --write-examples --write-inventory --json
```

Validate:

```text
python scripts/validate_seed_batch_manuals_scans.py
```

The runbook does not permit downloads, file fetches, OCR, extraction, live
source calls, model calls, public index mutation, deployment, or readiness
claims.
