# H4 Code Source Live Probe Result

The H4 live-probe result groups blocked/completed status, request count, network flag, normalized source/release metadata, source identity candidate, release identity candidate, source-to-binary relation preview, release asset metadata preview, source-cache preview, evidence preview, review seed preview, and connector health summary. Current examples are blocked/offline.

No-goals: broad source search, public query fanout, scraping, crawling, arbitrary URL fetches, model/provider calls, browser automation, product behavior changes, public/master index mutation, rights clearance, malware safety, verified authenticity, verified build reproducibility, installability, or production coverage claims.

Validation commands:
- `python scripts/validate_h4_code_source_live_probe.py`
- `python scripts/run_h4_code_source_live_probe.py --source-id github_releases --request-key example_release_metadata --check`
- `python scripts/summarize_h4_code_source_live_probe_outputs.py --input examples/connectors/h4_code_source_release/live_probe_results --check`
