# H4 Code Source Live Probe

H4 code/source/release live probes are bounded metadata observations. They default to offline preflight, require `--live`, and still fail closed unless committed per-source policy approves the exact request key and metadata class. They are not repository cloning, release asset fetching, source archive downloading, scraping, crawling, source sync, or truth acceptance.

No-goals: broad source search, public query fanout, scraping, crawling, arbitrary URL fetches, model/provider calls, browser automation, product behavior changes, public/master index mutation, rights clearance, malware safety, verified authenticity, verified build reproducibility, installability, or production coverage claims.

Validation commands:
- `python scripts/validate_h4_code_source_live_probe.py`
- `python scripts/run_h4_code_source_live_probe.py --source-id github_releases --request-key example_release_metadata --check`
- `python scripts/summarize_h4_code_source_live_probe_outputs.py --input examples/connectors/h4_code_source_release/live_probe_results --check`
