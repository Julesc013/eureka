# H7 Library Research Policy Gates

Every H7 source requires source policy approval, endpoint or metadata allowlist, User-Agent/contact posture where applicable, auth/no-auth posture, rate limit, timeout, retry budget, cache TTL, kill switch, fixture replay, output path policy, rights/access review, restricted-source review, review queue gate, post-run audit, and connector scorecard before live work.

## Current Boundary

H7-BUNDLE-01 is policy-pack-only. It does not enable live access, API queries,
OAI-PMH harvests, DOI/ISBN/patent queries, full-text fetches, downloads, IIIF
fetches, scraping, crawling, restricted-source access, source sync, public index
mutation, master index mutation, or truth acceptance.

## Validation

- `python scripts/validate_h7_library_research_policy_packs.py`
- `python scripts/summarize_h7_library_research_sources.py --check`
