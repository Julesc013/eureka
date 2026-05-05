# External Baseline Comparison

External Baseline Comparison v0 compares Eureka's current `local_index_only` search/public-index behavior against manually recorded external baseline observations.

It has a strict manual observation requirement: pending slots are not observations. The comparison script makes no web calls, no search-engine calls, no source API calls, no model calls, no scraping calls, and no hosted backend calls. This is a no-fabrication workflow.

Eligibility values:

- `no_observations`: no valid manual observations exist.
- `partial_observations`: some valid observations exist and some selected slots remain pending.
- `complete_batch`: a selected batch is fully observed before comparison synthesis.
- `invalid_observations`: baseline records failed validation.
- `local_search_unavailable`: local Eureka comparison could not run.
- `eligible`: records are ready for comparison.
- `comparison_completed`: comparison records were produced.

Run:

```powershell
python scripts/run_external_baseline_comparison.py --batch batch_0 --json
python scripts/validate_external_baseline_comparison_report.py
```

Add manual observations by following the external baseline schema and batch instructions under `evals/search_usefulness/external_baselines/`. Rerun `python scripts/validate_external_baseline_observations.py` before comparison.

Comparison dimensions include query/task match, exact artifact found, useful partial result, source coverage, compatibility evidence, representation/member access, provenance clarity, absence explanation, action safety, user effort, freshness, and not-comparable reason.

Labels: `eureka_better`, `baseline_better`, `both_good`, `both_partial`, `eureka_only`, `baseline_only`, `neither`, `not_comparable`, and `insufficient_data`.

The report is not a production claim and does not claim Eureka beats external systems without scoped evidence.
