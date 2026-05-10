# H7 Library Research No Live Call Policy

The current H7 bundle permits no live source calls, provider calls, model calls, endpoint probes, API queries, OAI-PMH harvesting, source sync, public-query fanout, or hosted behavior.

## Current Boundary

H7-BUNDLE-01 is policy-pack-only. It does not enable live access, API queries,
OAI-PMH harvests, DOI/ISBN/patent queries, full-text fetches, downloads, IIIF
fetches, scraping, crawling, restricted-source access, source sync, public index
mutation, master index mutation, or truth acceptance.

## Validation

- `python scripts/validate_h7_library_research_policy_packs.py`
- `python scripts/summarize_h7_library_research_sources.py --check`
