# H7 Library Research Fixture Plan

H7-BUNDLE-02 should add committed synthetic fixtures for minimal metadata records, typical source-specific records, identifier-rich records, citation/relation records, access/right/availability records, repository/deposit records, policy-blocked records, malformed/partial records, and no-live-call evidence. Fixtures must exclude credentials, full text, PDFs, scans, datasets, patents, IIIF payloads, media, OCR, restricted/licensed payloads, and scraping output.

## Current Boundary

H7-BUNDLE-01 is policy-pack-only. It does not enable live access, API queries,
OAI-PMH harvests, DOI/ISBN/patent queries, full-text fetches, downloads, IIIF
fetches, scraping, crawling, restricted-source access, source sync, public index
mutation, master index mutation, or truth acceptance.

## Validation

- `python scripts/validate_h7_library_research_policy_packs.py`
- `python scripts/summarize_h7_library_research_sources.py --check`
