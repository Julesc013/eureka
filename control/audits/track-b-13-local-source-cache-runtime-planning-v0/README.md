# TRACK-B-13 Local Source Cache Runtime Planning

TRACK-B-13 adds a planning and governance layer for a future local source cache.
It follows the candidate store runtime because candidates can point at possible
sources, but a separate source-cache plan is needed before any local source
observation storage or evidence bridge exists.

## Added

- Local source cache runtime plan and policies under
  `control/inventory/source_cache/`.
- Source access, path, record, review, and rollout gates.
- Public-safe source-cache plan examples.
- Planning docs and readiness report.
- Deterministic validator and operations tests.

## Runtime Boundary

Runtime is not implemented. Source access is disabled. No local source-cache
state is created. No source sync, live probes, scraping, crawling, arbitrary URL
fetch, downloads, uploads, accounts, telemetry, connector runtime, evidence
acceptance, public index use, or master-index mutation is enabled.

## Why This Prepares Evidence Ledger Planning

The future evidence ledger needs reviewed source observations, provenance,
privacy posture, and rights/risk boundaries. This plan keeps source-cache
records as observations until a later evidence-ledger bridge can turn reviewed
source-cache output into evidence candidates.

## Validation

```bash
python scripts/validate_local_source_cache_runtime_plan.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

## Next

TRACK-B-14 - Local evidence ledger runtime planning.
