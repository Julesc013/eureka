# Remaining Gaps

## Still Capability Gap

- `article_inside_magazine_scan`: no bounded article/page/OCR/scan fixture
  exists. This remains a true capability gap.

## Still Partial

At the time of Hard Eval Satisfaction Pack v0, the five moved tasks remained
partial because Eval Runner v0 still recorded but did not benchmark:

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

Follow-up status: Old-Platform Result Refinement Pack v0 is implemented under
`control/audits/old-platform-result-refinement-v0/`. It added deterministic
result-shape, expected-lane, and bad-result checks. `driver_inside_support_cd`
is now satisfied; the Firefox, FTP, Windows 98 registry repair, and Windows 7
app tasks remain partial with explicit evidence/result-shape limitations.

Further follow-up status: More Source Coverage Expansion v1 and Article/Scan
Fixture Pack v0 are now implemented. The current archive-resolution eval suite
reports `satisfied=6`, including source-backed article segment evidence for
`article_inside_magazine_scan`. This supersedes the original remaining hard
capability gap without weakening the task.

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
