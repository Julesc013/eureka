# TRACK-B-14 Local Evidence Ledger Runtime Planning

TRACK-B-14 adds a planning and governance layer for a future local evidence
ledger. It follows local source cache planning because source-cache observations
need a separate evidence-candidate boundary before they can inform candidate
promotion, pack export, review queues, public index use, or master-index review.

## Added

- Local evidence ledger runtime plan and policies under
  `control/inventory/evidence_ledger/`.
- Append-style planning policy.
- Source-cache-to-evidence bridge plan.
- Path, record, review, and rollout gates.
- Public-safe evidence-ledger plan examples.
- Planning docs and readiness report.
- Deterministic validator and operations tests.

## Runtime Boundary

Runtime is not implemented. Source-cache bridge runtime is not implemented.
Evidence acceptance is disabled. No local evidence-ledger state is created. No
evidence records are written. No source sync, live probes, scraping, crawling,
arbitrary URL fetch, downloads, uploads, accounts, telemetry, connector
runtime, public index use, or master-index mutation is enabled.

## Source-Cache Bridge Boundary

The bridge is future-only. It can only produce evidence candidates and
provenance links after review. It cannot convert source observations, AI drafts,
contribution claims, metadata claims, checksum claims, or compatibility claims
into accepted truth or master-index material.

## Validation

```bash
python scripts/validate_local_evidence_ledger_runtime_plan.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

## Next

TRACK-B-15 - Local source cache runtime.
