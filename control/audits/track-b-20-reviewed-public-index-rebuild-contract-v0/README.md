# TRACK-B-20 Reviewed Public Index Rebuild Contract

This audit pack records the B20 contract-only milestone.

## Added

- Reviewed public-index rebuild contract.
- Reviewed public record proposal contract.
- Review policies for rebuild inputs, outputs, records, paths, and truth boundaries.
- Public-safe rebuild and proposal examples.
- Contract validator and contract tests.
- Reference, architecture, and operations documentation.

## Why This Follows Promotion Dry-Run

Candidate promotion dry-run rehearses whether a candidate may be ready for a future reviewed record proposal. B20 defines the contract for those future proposals and rebuild manifests while keeping all public-index mutation disabled.

## Runtime Boundary

No public-index rebuild runtime was implemented. No public index, master index, `site/dist/`, or `data/public_index/` files were mutated.

## Review Gates

Future rebuild work must preserve evidence, review, source, conflict, duplicate, rights, risk, compatibility, identity, and limitation posture. Ready statuses remain future dry-run eligibility only.

## Validation

```bash
python scripts/validate_reviewed_public_index_rebuild_contract.py
python -m unittest tests.contracts.test_reviewed_public_index_rebuild_contract
python scripts/check_architecture_boundaries.py
```

## No-Goals

No candidate acceptance, evidence acceptance, public truth creation, hosted moderation, live source access, source sync, downloads, uploads, accounts, telemetry, provider calls, public-index mutation, or master-index mutation.

## Next Task

TRACK-B-21 - Pack builder runtime.
