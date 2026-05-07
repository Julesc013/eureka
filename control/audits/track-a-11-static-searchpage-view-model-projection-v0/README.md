# TRACK-A-11 Static SearchPage Projection Audit

## What Was Added

- A read-only static SearchPage projection map at
  `control/inventory/publication/search_page_static_projection_map.json`.
- A deterministic audit script at
  `scripts/audit_static_searchpage_projection.py`.
- Operation notes at
  `docs/operations/STATIC_SEARCHPAGE_VIEW_MODEL_PROJECTION_AUDIT.md`.
- Unit coverage at
  `tests/operations/test_static_searchpage_projection_audit.py`.
- This audit pack with a JSON report, gap report, and validation notes.

## Why This Supports Track A

Track A established `SearchPageView` as the canonical meaning layer. This audit
records how the existing static SearchPage artifacts currently preserve that
meaning and where later renderer/generator work must bridge gaps.

## What Remains Deferred

- Creating a canonical SearchPageView fixture for the static handoff.
- Generating standard, lite, text, file-tree, and JSON projections from that
  fixture.
- Replacing or refactoring any existing `site/dist` artifacts.
- Hosted public search, live probes, source connectors, downloads, accounts,
  telemetry, native clients, and public route activation.

## Validation Commands

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/publication/search_page_static_projection_map.json`
- `python -m json.tool control/audits/track-a-11-static-searchpage-view-model-projection-v0/projection_audit_report.json`
- `python scripts/validate_track_a_contracts.py`
- `python scripts/audit_static_searchpage_projection.py --check`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- AIDE Lite `doctor`, `validate`, `test`, `selftest`, `verify`, `eval list`,
  `eval run`, `review-pack`, and `adapter validate`

## No-Goals Preserved

No product runtime behavior changed. No static site was regenerated. No public
routes, hosted behavior, live probes, source sync, connectors, downloads,
uploads, accounts, telemetry, native projects, or master-index behavior were
enabled.

## Next Task Recommendation

`TRACK-A-12 - Static SearchPage projection fixture and generator plan`
