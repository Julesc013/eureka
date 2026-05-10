# H6 Web Archive Review Integration Model

The model keeps control, contracts, runtime helpers, examples, and audit outputs separate. Runtime helpers are standard-library-only and consume local JSON artifacts without network, CDX/Memento, WARC/WACZ, page, media, document, scrape, crawl, browser, bypass, or sensitive-source access.

No-goals: no new live calls, CDX/Memento queries, WARC/WACZ fetches, archived/live page fetches, media/transcript/newspaper/public-document downloads, scraping, crawling, browser automation, bypass, sensitive-source access, source sync, public/master index mutation, production claims, or truth acceptance.

Fixture/live/blocked handling: committed fixtures and replay outputs may create review seeds; blocked live-probe reports are policy evidence only; approved live-probe outputs, if present in a future task, remain candidates/previews until reviewed.

Validation commands:

- `python scripts/validate_h6_web_archive_review_quality_audit.py`
- `python scripts/integrate_h6_web_archive_review.py --input-dir examples/connectors/h6_web_archive_news_event/replay_results --check`
- `python scripts/summarize_h6_web_archive_quality_delta.py --input-dir examples/connectors/h6_web_archive_news_event/review_integration --check`
- `python scripts/audit_h6_web_archive_news_event_wave.py --check`
