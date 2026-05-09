# Validation

H1-BUNDLE-03 validation completed with blocked live probes. The framework, examples, tests, and inherited validators pass; no source has committed operator approval, so live probes remain blocked before network.

## Results

- `git diff --check`: PASS
- H1 live-probe contract and policy JSON syntax: PASS
- `python scripts/validate_h1_metadata_live_probe.py`: PASS
- `python scripts/run_h1_metadata_live_probe.py --source-id pypi --request-key example_project_metadata --check`: PASS
- `python scripts/summarize_h1_live_probe_outputs.py --input examples/connectors/h1_metadata_wave/live_probe_results --check`: PASS
- `python -m unittest tests.connectors.test_h1_metadata_live_probe`: PASS
- `python -m unittest tests.operations.test_h1_metadata_live_probe_scripts`: PASS
- `python -m unittest discover -s tests -t .`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- Existing H0/H1/IA/core validators: PASS
- AIDE Lite doctor, validate, test, selftest, eval list, eval run, review-pack, adapter validate: PASS
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, limited to existing optional review-packet references for missing controller/gateway/provider status artifacts.

## Live Probe Outcome

- attempted_sources: none
- completed_sources: none
- blocked_sources: wayback_cdx_memento, github_releases, pypi, npm_registry, software_heritage, repology, osv
- request_count_total: 0
- network_used: false
- reason_if_blocked: missing committed operator approval for source-specific metadata probes
