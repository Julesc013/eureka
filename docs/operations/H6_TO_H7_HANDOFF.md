# H6 To H7 Handoff

H6 recommends H7-BUNDLE-01 when the web archive/news/event wave is coherent. H7 should begin with policy-pack-only library, cultural, book, and research source-family work and preserve no-live/no-truth boundaries.

No-goals: no new live calls, CDX/Memento queries, WARC/WACZ fetches, archived/live page fetches, media/transcript/newspaper/public-document downloads, scraping, crawling, browser automation, bypass, sensitive-source access, source sync, public/master index mutation, production claims, or truth acceptance.

Fixture/live/blocked handling: committed fixtures and replay outputs may create review seeds; blocked live-probe reports are policy evidence only; approved live-probe outputs, if present in a future task, remain candidates/previews until reviewed.

Validation commands:

- `python scripts/validate_h6_web_archive_review_quality_audit.py`
- `python scripts/integrate_h6_web_archive_review.py --input-dir examples/connectors/h6_web_archive_news_event/replay_results --check`
- `python scripts/summarize_h6_web_archive_quality_delta.py --input-dir examples/connectors/h6_web_archive_news_event/review_integration --check`
- `python scripts/audit_h6_web_archive_news_event_wave.py --check`
