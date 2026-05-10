# H7 Access Rights Availability Policy

Access, rights, and availability candidates include access status, open-access status, license metadata, rights statements, landing pages, full-text URL candidates, embargoes, restricted access, and account/paywall signals. They are not rights clearance.

## Current Boundary

H7-BUNDLE-01 is policy-pack-only. It does not enable live access, API queries,
OAI-PMH harvests, DOI/ISBN/patent queries, full-text fetches, downloads, IIIF
fetches, scraping, crawling, restricted-source access, source sync, public index
mutation, master index mutation, or truth acceptance.

## Validation

- `python scripts/validate_h7_library_research_policy_packs.py`
- `python scripts/summarize_h7_library_research_sources.py --check`
