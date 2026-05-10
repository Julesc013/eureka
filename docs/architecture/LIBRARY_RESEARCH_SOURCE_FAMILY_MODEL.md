# Library Research Source Family Model

Library/cultural/research sources are metadata and identity sources first. They can support fixture-only normalization of bibliographic, research, dataset, cultural, patent, citation, and access-rights candidates in H7-BUNDLE-02.

## Current Boundary

H7-BUNDLE-01 is policy-pack-only. It does not enable live access, API queries,
OAI-PMH harvests, DOI/ISBN/patent queries, full-text fetches, downloads, IIIF
fetches, scraping, crawling, restricted-source access, source sync, public index
mutation, master index mutation, or truth acceptance.

## Validation

- `python scripts/validate_h7_library_research_policy_packs.py`
- `python scripts/summarize_h7_library_research_sources.py --check`
