# Validation

- `python scripts/validate_ranking_shadow_runtime.py`: PASS
- `python scripts/run_ranking_shadow.py --input examples/search/quality/ranking/input_bundle_software_v0.json --check`: PASS
- `python scripts/run_search_quality_regression.py --query-set examples/search/quality/query_sets/minimal_search_quality_query_set_v0.json --check`: PASS
- `python scripts/summarize_ranking_shadow.py --input examples/search/quality/ranking --check`: PASS
- `python -m unittest discover -s tests -t .`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
