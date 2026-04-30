# Static Site Evidence

- path: `site/dist/`
- validator command: `python scripts/validate_public_static_site.py`
- validator status: `valid`

The validator confirms required pages, local links, current source IDs, required cautionary claims, prohibited-claim absence, no-JS posture, and public-alpha limitation coverage.

Required cautionary claims include Python reference backend prototype, not production, no scraping, external baselines pending/manual, and placeholders remain placeholders.

The static site pack is static-only. GitHub Pages may upload it through the configured workflow after validation, but the artifact itself starts no server and hosts no Python backend.

