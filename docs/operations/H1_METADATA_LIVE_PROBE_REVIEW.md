# H1 Metadata Live Probe Review

All source-cache, evidence, review seed, and health outputs require review before downstream use.

## Not Goals

- No broad search, scraping, crawling, downloads, source sync, public query fanout, index mutation, truth acceptance, rights clearance, malware safety, verified installability, or production readiness claim.

## Validation

- `python scripts/validate_h1_metadata_live_probe.py`
- `python scripts/run_h1_metadata_live_probe.py --source-id pypi --request-key example_project_metadata --check`
- `python scripts/summarize_h1_live_probe_outputs.py --input examples/connectors/h1_metadata_wave/live_probe_results --check`
