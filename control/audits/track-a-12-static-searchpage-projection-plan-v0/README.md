# TRACK-A-12 Static SearchPage Projection Plan

This audit pack records the narrow generator plan and canonical fixture needed
before TRACK-A-13 can perform a dry run.

## Added

- `control/inventory/publication/search_page_static_projection_plan.json`
- `examples/view_models/search_page/static_projection_reference_v0.json`
- `docs/operations/STATIC_SEARCHPAGE_PROJECTION_GENERATOR_PLAN.md`
- `scripts/validate_static_searchpage_projection_plan.py`

## Why

The A11 audit found that current static SearchPage artifacts are not traced to
one canonical `SearchPageView`. A12 defines the fixture, output-root boundary,
and projection target vocabulary that A13 uses.

## No-Goals

No `site/dist` files are generated or changed. No runtime, hosted backend, live
probe, source connector, download, upload, account, telemetry, native, or
master-index behavior is enabled.

## Validation

- `python scripts/validate_static_searchpage_projection_plan.py`

## Next

- TRACK-A-13 - Static SearchPage projection dry-run generator
