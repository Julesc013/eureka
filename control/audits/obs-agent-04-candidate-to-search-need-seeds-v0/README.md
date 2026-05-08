# OBS-AGENT-04 Candidate To SearchNeed Seeds

## What Was Added

This audit packet records the OBS side-lane SearchNeed seed draft layer:

- Query contracts for `search_need_seed.v0` and `search_need_seed_conversion.v0`
- Conversion policy, priority model, and deterministic seed manifest
- Public-safe seed and conversion examples
- Build, validate, and summarize scripts
- Tests covering draft-only boundaries and no external access behavior

## OBS Lane Boundary

This work is governance and planning material. It differs from Track B by
producing draft seed records only. It does not create runtime SearchNeed
records, WorkUnits, source connectors, source sync, evidence truth, observed
baselines, public routes, or product behavior.

## How Seeds Are Built

The build script reads committed repo-local examples and the OBS-03 review
queue. It emits a deterministic manifest of five SearchNeed seed drafts:

- One source-gap seed
- One extraction-gap seed
- One compatibility-gap seed
- One manual-observation seed
- One policy-blocked seed

## Review Gate

All seeds require human review. A seed is not a runtime SearchNeed, not an
observed baseline, not accepted evidence, not source approval, and not a
master-index change.

## Validation

```powershell
python scripts/build_search_need_seed_candidates.py --list-inputs
python scripts/build_search_need_seed_candidates.py --check
python scripts/validate_search_need_seed_candidates.py
python scripts/summarize_search_need_seed_candidates.py
python -m unittest tests.contracts.test_search_need_seed_contracts tests.operations.test_search_need_seed_conversion
```

## No Goals

- No live external searches.
- No browser automation.
- No API calls.
- No scraping or crawling.
- No runtime SearchNeed creation.
- No source approval.
- No observed baseline or evidence truth.
- No Track B runtime mutation.

## Next Task

OBS-AGENT-05 - Candidate-to-WorkUnit seed conversion.
