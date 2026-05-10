# H4 Code Source Live Probe No Clone Download Policy

H4 live probes forbid repository clone/fetch/ls-remote, source archive downloads, release asset downloads, binaries, installers, checksums, signatures, SBOM payloads, git commands, build tools, package managers, install, and execution. Metadata fields about assets do not grant payload access.

No-goals: broad source search, public query fanout, scraping, crawling, arbitrary URL fetches, model/provider calls, browser automation, product behavior changes, public/master index mutation, rights clearance, malware safety, verified authenticity, verified build reproducibility, installability, or production coverage claims.

Validation commands:
- `python scripts/validate_h4_code_source_live_probe.py`
- `python scripts/run_h4_code_source_live_probe.py --source-id github_releases --request-key example_release_metadata --check`
- `python scripts/summarize_h4_code_source_live_probe_outputs.py --input examples/connectors/h4_code_source_release/live_probe_results --check`
