# TRACK-A-16 Renderer Parity Harness

This audit adds the Track A renderer parity harness.

## Added

- Renderer parity harness contract.
- Renderer parity harness policy inventory.
- Renderer parity check matrix.
- SearchPage current parity case.
- ObjectPage and SourcePage future placeholder cases, plus NeedPage and CandidatePage inline future placeholders in the matrix.
- Validator and runner scripts.
- Contract and operations docs.
- Audit reports for the current run.

## Why This Follows Design Tokens

TRACK-A-15 defined presentation tokens and Temporal Minimal Search doctrine. TRACK-A-16 adds the governed check that future renderers must pass: presentation may degrade, but semantic meaning and product-boundary posture must remain intact.

## Current Check

The active SearchPage case checks the TRACK-A-13 dry-run outputs under `control/audits/track-a-13-static-searchpage-projection-dry-run-v0/generated/`.

The harness checks required text markers, required JSON paths, forbidden text markers, forbidden JSON claims, and product-boundary non-claims.

## Future Cases

ObjectPage, SourcePage, NeedPage, and CandidatePage are recorded as future or no-active-output cases. They are skipped by the runner until later projection dry-runs exist.

## Validation

```powershell
python -m json.tool control/inventory/publication/renderer_parity_harness_policy.json
python -m json.tool control/inventory/publication/renderer_parity_check_matrix.json
python -m json.tool control/audits/track-a-16-renderer-parity-harness-v0/renderer_parity_report.json
python scripts/validate_renderer_parity_harness.py
python scripts/run_renderer_parity_harness.py --list
python scripts/run_renderer_parity_harness.py --check
python scripts/validate_track_a_contracts.py
python -m unittest discover -s tests -t .
python scripts/check_architecture_boundaries.py
```

## No-Goals

- No static site refactor.
- No `site/dist` regeneration.
- No renderer implementation beyond audit and validation checks.
- No hosted backend, live probes, source connectors, downloads, uploads, accounts, telemetry, native runtime, node runtime, pack import runtime, review runtime, or master-index mutation.
- No rights clearance, malware safety, verified installability, exhaustive search, automatic promotion, or Google affiliation claim.

## Next

TRACK-A-17 - Track A integration audit.
