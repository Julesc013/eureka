# TRACK-B-15 Local Source Cache Runtime

This audit pack records the first fixture-only local source cache runtime for Track B.

## Added

- `runtime/local/foundry/source_cache.py`
- `scripts/record_source_cache.py`
- `scripts/summarize_source_cache.py`
- `scripts/validate_local_source_cache_runtime.py`
- source cache runtime policies, examples, docs, and tests
- generated audit sample from committed source-cache examples

## Boundary

The runtime records explicit fixture/repo-local observations only. It does not fetch sources, run source sync, enable connectors, call APIs, call networks, call models, write private local state, write evidence records, or mutate the master index.

Source cache records are review-gated observations. They are not evidence truth, public truth, rights clearance, malware safety, installability proof, or production-readiness evidence.

## Validation

Primary commands:

```bash
python scripts/validate_local_source_cache_runtime_plan.py
python scripts/validate_local_evidence_ledger_runtime_plan.py
python scripts/validate_local_source_cache_runtime.py
python scripts/record_source_cache.py --input examples/sources/cache/records/source_lead_record_v0.json --check
python scripts/summarize_source_cache.py --input examples/sources/cache/records --check
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

## Next

Recommended next task: `TRACK-B-16 — Local evidence ledger runtime`.
