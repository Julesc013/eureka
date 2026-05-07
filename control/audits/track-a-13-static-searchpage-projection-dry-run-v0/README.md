# TRACK-A-13 Static SearchPage Projection Dry Run

This audit pack contains dry-run SearchPage projection evidence generated from
one canonical `SearchPageView` fixture.

## Generated

The generator wrote preview artifacts only under this audit directory:

- `generated/search.standard.html`
- `generated/search.lite.html`
- `generated/search.txt`
- `generated/search.README.txt`
- `generated/search_handoff.json`

The source fixture is
`examples/view_models/search_page/static_projection_reference_v0.json`.

## Why This Is Evidence Only

These files prove projection feasibility. They are not the active public site,
not deployment artifacts, not live API output, and not production claims.
`site/dist` was not regenerated or changed.

## Preserved Semantics

The dry run preserves route identity, query identity, public runtime posture,
result identity, source/evidence posture, rights/risk posture, compatibility
posture, limitations, blocked actions, and next safe actions. File-tree output
degrades result/source detail into README form while preserving status and
caveats.

## Deferred

- Diffing generated previews against current `site/dist` artifacts.
- Replacing or refactoring current static site generation.
- Hosted search, live probes, downloads, uploads, accounts, telemetry, native
  clients, or runtime renderer binding.

## Validation

- `python scripts/generate_static_searchpage_projection.py --check`
- `python scripts/validate_static_searchpage_projection_dry_run.py`
- `python scripts/validate_static_searchpage_projection_plan.py`
- `python scripts/audit_static_searchpage_projection.py --check`
- `python scripts/validate_track_a_contracts.py`
- `python -m unittest discover -s tests -t .`

## No-Goals

No product runtime behavior, public route activation, hosted backend, live
source behavior, source connectors, downloads, installers, execution, uploads,
accounts, telemetry, native project, master-index mutation, or generated site
artifact mutation was added.

## Next

- TRACK-A-14 - Object Source Need Candidate projection audit
