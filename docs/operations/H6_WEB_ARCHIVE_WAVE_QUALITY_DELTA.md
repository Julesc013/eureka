# H6 Web Archive Wave Quality Delta

Quality delta values are counts and review-readiness notes only. They must not be interpreted as production search quality, archive coverage, capture completeness, event truth, article truth, public-document truth, rights clearance, privacy safety, malware safety, authenticity, or production readiness.

No-goals: no new live calls, CDX/Memento queries, WARC/WACZ fetches, archived/live page fetches, media/transcript/newspaper/public-document downloads, scraping, crawling, browser automation, bypass, sensitive-source access, source sync, public/master index mutation, production claims, or truth acceptance.

Fixture/live/blocked handling: committed fixtures and replay outputs may create review seeds; blocked live-probe reports are policy evidence only; approved live-probe outputs, if present in a future task, remain candidates/previews until reviewed.

Validation commands:

- `python scripts/validate_h6_web_archive_review_quality_audit.py`
- `python scripts/integrate_h6_web_archive_review.py --input-dir examples/connectors/h6_web_archive_news_event/replay_results --check`
- `python scripts/summarize_h6_web_archive_quality_delta.py --input-dir examples/connectors/h6_web_archive_news_event/review_integration --check`
- `python scripts/audit_h6_web_archive_news_event_wave.py --check`
