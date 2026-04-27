# More Source Coverage Expansion v1

This audit pack records the bounded source-fixture expansion after Old-Platform Result Refinement Pack v0.

The pack targets the four remaining old-platform hard-eval partials:

- `latest_firefox_before_xp_drop`
- `old_blue_ftp_client_xp`
- `win98_registry_repair`
- `windows_7_apps`

It adds tiny recorded/fixture-only source material under existing active fixture families. It does not add live source calls, scraping, crawling, arbitrary local filesystem ingestion, new connector families, real binaries, external baseline observations, or deployment behavior.

The remaining `article_inside_magazine_scan` capability gap was intentionally
left for a future Article/Scan Fixture Pack. Follow-up status: Article/Scan
Fixture Pack v0 is now implemented under
`control/audits/article-scan-fixture-pack-v0/`.
