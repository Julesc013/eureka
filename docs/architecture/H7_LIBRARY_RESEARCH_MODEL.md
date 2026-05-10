# H7 Library Research Model

The H7 model groups library catalog, OAI-PMH, research graph, research repository, dataset repository, cultural repository, patent metadata, and restricted manifest-only families. It reuses H0-H6 Source OS patterns for source records, policy packs, coverage previews, scorecards, and audit evidence.

## Current Boundary

H7-BUNDLE-01 is policy-pack-only. It does not enable live access, API queries,
OAI-PMH harvests, DOI/ISBN/patent queries, full-text fetches, downloads, IIIF
fetches, scraping, crawling, restricted-source access, source sync, public index
mutation, master index mutation, or truth acceptance.

## Validation

- `python scripts/validate_h7_library_research_policy_packs.py`
- `python scripts/summarize_h7_library_research_sources.py --check`
