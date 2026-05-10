# H4 Code Source Live Probe Approval Gates

Before a source call, policy must approve live_access, metadata_probe, exact request key, metadata class allowlist, user-agent/contact or not-required posture, auth/no-auth posture, timeout, retry budget, cache decision, kill switch, and output path. Clone, download, git, build, install, execution, scraping, crawling, source sync, and fanout approvals must remain false.

No-goals: broad source search, public query fanout, scraping, crawling, arbitrary URL fetches, model/provider calls, browser automation, product behavior changes, public/master index mutation, rights clearance, malware safety, verified authenticity, verified build reproducibility, installability, or production coverage claims.

Validation commands:
- `python scripts/validate_h4_code_source_live_probe.py`
- `python scripts/run_h4_code_source_live_probe.py --source-id github_releases --request-key example_release_metadata --check`
- `python scripts/summarize_h4_code_source_live_probe_outputs.py --input examples/connectors/h4_code_source_release/live_probe_results --check`
