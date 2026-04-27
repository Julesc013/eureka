# Remaining Gaps

## Still Capability Gap

- `article_inside_magazine_scan`: no bounded article/page/OCR/scan fixture
  exists. This remains a true capability gap.

## Still Partial

The five moved tasks remain partial because Eval Runner v0 still records but
does not benchmark:

- expected result lanes
- bad-result pattern avoidance
- production-style result ordering
- final best-answer selection

## Task-Specific Gaps

- `latest_firefox_before_xp_drop`: needs exact latest-compatible release
  evidence and a direct artifact/release asset trace.
- `old_blue_ftp_client_xp`: needs a concrete source-backed product identity or
  direct installer/member artifact.
- `driver_inside_support_cd`: needs future lane/bad-result scoring before it
  can be satisfied overall.
- `win98_registry_repair`: needs future lane/bad-result scoring before it can
  be satisfied overall.
- `windows_7_apps`: needs future lane/bad-result scoring and broader result
  refinement before it can be satisfied overall.

## Still Deferred

- live crawling
- Google scraping
- Internet Archive scraping or live API calls
- arbitrary local filesystem ingestion
- fuzzy/vector/LLM retrieval
- production ranking
- Rust behavior ports
- native apps
- production deployment infrastructure
- external baseline claims
