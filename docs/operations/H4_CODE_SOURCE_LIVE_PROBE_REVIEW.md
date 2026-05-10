# H4 Code Source Live Probe Review

H4 live-probe outputs require review before source cache persistence, evidence acceptance, candidate acceptance, source identity acceptance, release identity acceptance, source-to-binary relation acceptance, public index use, or master index use.

No-goals: broad source search, public query fanout, scraping, crawling, arbitrary URL fetches, model/provider calls, browser automation, product behavior changes, public/master index mutation, rights clearance, malware safety, verified authenticity, verified build reproducibility, installability, or production coverage claims.

Validation commands:
- `python scripts/validate_h4_code_source_live_probe.py`
- `python scripts/run_h4_code_source_live_probe.py --source-id github_releases --request-key example_release_metadata --check`
- `python scripts/summarize_h4_code_source_live_probe_outputs.py --input examples/connectors/h4_code_source_release/live_probe_results --check`
