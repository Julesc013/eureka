# Static SearchPage Projection Generator Plan

TRACK-A-12 defines the dry-run shape for projecting one canonical
`SearchPageView` fixture into static-compatible outputs.

## Purpose

The plan proves, before any site refactor, that SearchPage meaning can be
rendered as standard HTML, lite HTML, plain text, a file-tree README, and a
static JSON handoff without changing route identity or source/evidence/status
meaning.

## Source Fixture

- `examples/view_models/search_page/static_projection_reference_v0.json`

The fixture is public-safe, anonymous/no-retention, and static-handoff only.
It includes a candidate result so projections must preserve candidate status,
source/evidence posture, rights/risk uncertainty, limitations, and blocked
actions.

## Output Policy

Generated previews are allowed only under audit or scratch roots:

- `control/audits/**`
- `.aide/reports/**`
- temporary paths outside the repo

The generator must reject `site/dist`, runtime, contracts, canonical inventory,
surface, native, and other product/runtime roots.

## Deferred Work

- No `site/dist` replacement.
- No static template refactor.
- No hosted backend or live source behavior.
- No downloads, installs, uploads, accounts, telemetry, native project, or
  master-index mutation.

## Validation

```powershell
python scripts/validate_static_searchpage_projection_plan.py
python scripts/generate_static_searchpage_projection.py --check
python scripts/validate_static_searchpage_projection_dry_run.py
```
