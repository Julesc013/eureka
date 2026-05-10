# H6 Web Archive Live Probe

Defines fail-closed metadata-only probe envelopes for web archive, news, event, and public trace sources.

Current H6-BUNDLE-03 behavior is offline by default. The CLI performs dry preflight and emits blocked output unless committed source policy explicitly approves a bounded metadata-only request and `--live` is provided.

Allowed outputs are live-probe results, normalized trace records, candidate previews, source-cache previews, evidence previews, review queue seed previews, and connector health summaries. These outputs do not accept source truth, evidence truth, web capture truth, time-state truth, event truth, article truth, public-document truth, authenticity, rights, privacy, safety, or production coverage.

Forbidden behavior remains: broad search, public-query fanout, CDX/Memento lookup without exact approval, WARC/WACZ fetch, archived or live page fetch, media or transcript download, public-document fetch, restricted-source access, scraping, crawling, browser automation, bypass, source sync, public index mutation, and master index mutation.

Validation:

- `python scripts/validate_h6_web_archive_live_probe.py`
- `python scripts/run_h6_web_archive_live_probe.py --source-id wayback_cdx_memento --request-key example_capture_metadata --check`
- `python scripts/summarize_h6_web_archive_live_probe_outputs.py --input examples/connectors/h6_web_archive_news_event/live_probe_results --check`
