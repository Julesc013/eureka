# H2 Package Live Probe Approval Gates

H2-BUNDLE-03 defines a bounded metadata-only live-probe framework for Maven Central, NuGet, crates.io, RubyGems, CPAN, CRAN, conda-forge, and OCI registry metadata.

Current behavior is fail-closed. Default commands run offline preflight or blocked-output paths, and `--live` cannot make a network call unless committed source-specific policy approves the exact source, request key, endpoint class, rate, cache, timeout, retry, kill switch, and output path gates.

The framework may produce live probe results, normalized package metadata records, package identity candidates, dependency candidates, file/hash candidates, source-cache previews, evidence previews, review queue seed previews, connector health summaries, coverage previews, and scorecard previews.

It does not produce accepted package identity truth, source truth, evidence truth, candidate truth, public records, public-index mutation, master-index mutation, download permission, installability verification, dependency correctness proof, rights clearance, malware safety, or production readiness.

Downloads, source archive fetches, OCI layer pulls, package-manager invocation, install, execute, scraping, crawling, source sync, and public-query fanout remain forbidden.

Validation:

- `python scripts/validate_h2_package_live_probe.py`
- `python scripts/run_h2_package_live_probe.py --source-id crates_io --request-key example_package_metadata --check`
- `python scripts/summarize_h2_package_live_probe_outputs.py --input examples/connectors/h2_package_registries/live_probe_results --check`
