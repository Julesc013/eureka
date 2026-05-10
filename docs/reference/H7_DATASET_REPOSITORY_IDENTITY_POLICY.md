# H7 Dataset Repository Identity Policy

Dataset identity candidates include repository record IDs, DataCite/DOI metadata, versions, distribution metadata, licenses, related publications, sizes, and checksums. They do not prove data validity, rights clearance, download permission, or malware safety.

## Current Boundary

H7-BUNDLE-01 is policy-pack-only. It does not enable live access, API queries,
OAI-PMH harvests, DOI/ISBN/patent queries, full-text fetches, downloads, IIIF
fetches, scraping, crawling, restricted-source access, source sync, public index
mutation, master index mutation, or truth acceptance.

## Validation

- `python scripts/validate_h7_library_research_policy_packs.py`
- `python scripts/summarize_h7_library_research_sources.py --check`
