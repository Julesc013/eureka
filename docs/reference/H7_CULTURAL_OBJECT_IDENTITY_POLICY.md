# H7 Cultural Object Identity Policy

Cultural object candidates include object title, creator or institution, collection IDs, object type, dates, places, rights statements, IIIF refs, media refs, and related works. IIIF or media references do not grant fetch or download permission.

## Current Boundary

H7-BUNDLE-01 is policy-pack-only. It does not enable live access, API queries,
OAI-PMH harvests, DOI/ISBN/patent queries, full-text fetches, downloads, IIIF
fetches, scraping, crawling, restricted-source access, source sync, public index
mutation, master index mutation, or truth acceptance.

## Validation

- `python scripts/validate_h7_library_research_policy_packs.py`
- `python scripts/summarize_h7_library_research_sources.py --check`
