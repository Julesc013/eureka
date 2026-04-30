# Local Validation Evidence

Local validation was run on `2026-04-30T15:23:14Z` from the synced `main` checkout.

Passed checks:

- `python scripts/validate_repository_layout.py`
- `python scripts/validate_static_artifact_promotion_review.py`
- `python site/build.py --check`
- `python site/validate.py`
- `python scripts/check_github_pages_static_artifact.py --path site/dist`
- `python scripts/check_generated_artifact_drift.py --artifact static_site_dist`
- `python scripts/validate_publication_inventory.py`
- `python scripts/validate_public_static_site.py --site-root site/dist`

Result:

Local artifact readiness is valid. The failure observed in GitHub Actions occurs after
local artifact generation and validation, at GitHub Pages configuration time.
