# TRACK-B-16 Local Evidence Ledger Runtime

This audit pack records the first fixture-only local evidence ledger runtime for Track B.

## Added

- `runtime/local/foundry/evidence_ledger.py`
- `scripts/record_evidence_ledger.py`
- `scripts/summarize_evidence_ledger.py`
- `scripts/validate_local_evidence_ledger_runtime.py`
- evidence ledger runtime policies, examples, docs, tests, and generated audit evidence

## Boundary

The runtime records explicit fixture/repo-local evidence candidates only. It does not accept evidence, create public records, implement the source-cache-to-evidence bridge, fetch sources, run source sync, enable connectors, call APIs, call networks, call models, write private local state, or mutate the master index.

Evidence records are review-gated candidates and provenance events. They are not public truth, rights clearance, malware safety, installability proof, or production-readiness evidence.

## Validation

Primary commands:

```bash
python scripts/validate_local_evidence_ledger_runtime_plan.py
python scripts/validate_local_source_cache_runtime.py
python scripts/validate_local_evidence_ledger_runtime.py
python scripts/record_evidence_ledger.py --input examples/evidence/ledger/records/metadata_claim_record_v0.json --check
python scripts/summarize_evidence_ledger.py --input examples/evidence/ledger/records --check
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

## Next

Recommended next task: `TRACK-B-17 — Source cache to evidence ledger bridge`.
