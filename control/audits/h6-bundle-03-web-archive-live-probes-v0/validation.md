# Validation

Validation commands were run locally with offline defaults:

- `git diff --check`: PASS
- `python -m json.tool` for required H6 contracts, policies, and audit report: PASS
- `python scripts/validate_h6_web_archive_live_probe.py`: PASS
- `python scripts/run_h6_web_archive_live_probe.py --source-id wayback_cdx_memento --request-key example_capture_metadata --check`: PASS
- `python scripts/summarize_h6_web_archive_live_probe_outputs.py --input examples/connectors/h6_web_archive_news_event/live_probe_results --check`: PASS
- `python -m unittest tests.connectors.test_h6_web_archive_live_probe`: PASS
- `python -m unittest tests.operations.test_h6_web_archive_live_probe_scripts`: PASS
- `python -m unittest discover -s tests -t .`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- Existing H6/H5/H4/H3/H2/H1/H0/core validator sweep: PASS
- AIDE Lite doctor/validate/test/selftest/eval/review-pack/adapter validate: PASS
- AIDE Lite verify: WARN-only with 0 errors

- network_used: `false`
- warc_wacz_fetch: `false`
- archived_page_fetch: `false`
- scraping_crawling: `false`
- restricted_source_access: `false`
- public_index_mutated: `false`
- master_index_mutated: `false`
- truth_acceptance: `false`
