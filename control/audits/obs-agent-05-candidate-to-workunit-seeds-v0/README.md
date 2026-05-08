# OBS-AGENT-05 Candidate To WorkUnit Seeds

## What Was Added

This audit packet records the OBS side-lane WorkUnit seed draft layer:

- Query contracts for `workunit_seed.v0` and `workunit_seed_conversion.v0`
- Conversion policy, priority model, and deterministic seed manifest
- Public-safe WorkUnit seed and conversion examples
- Build, validate, and summarize scripts
- Tests covering non-executable boundaries and no external access behavior

## OBS Lane Boundary

This work is governance and planning material. It differs from Track B by
producing draft seed records only. It does not create runtime WorkUnits, execute
work, create source connectors, source sync, evidence truth, observed baselines,
public routes, or product behavior.

## How Seeds Are Built

The build script reads committed repo-local examples, the OBS-03 review queue,
and the OBS-04 SearchNeed seed manifest. It emits a deterministic manifest of
six WorkUnit seed drafts:

- One SearchNeed review seed
- One source policy review seed
- One metadata probe planning seed
- One extraction gap planning seed
- One compatibility evidence review seed
- One policy-blocked review seed

## Review Gate

All seeds require human review. A WorkUnit seed is not executable, not a runtime
WorkUnit, not an observed baseline, not accepted evidence, not source approval,
and not a master-index change.

## Validation

```powershell
python scripts/build_workunit_seed_candidates.py --list-inputs
python scripts/build_workunit_seed_candidates.py --check
python scripts/validate_workunit_seed_candidates.py
python scripts/summarize_workunit_seed_candidates.py
python -m unittest tests.contracts.test_workunit_seed_contracts tests.operations.test_workunit_seed_conversion
```

## No Goals

- No live external searches.
- No browser automation.
- No API calls.
- No scraping or crawling.
- No WorkUnit execution.
- No runtime WorkUnit creation.
- No source approval.
- No observed baseline or evidence truth.
- No Track B runtime mutation.

## Next Task

OBS-AGENT-06 - OBS and Track B synchronization audit.
