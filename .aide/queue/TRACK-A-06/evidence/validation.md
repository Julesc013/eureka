# TRACK-A-06 Validation Evidence

Observed validation:

- `python -m json.tool control/inventory/publication/source_page_view_model_policy.json`
- `python -m json.tool control/audits/track-a-06-source-page-view-model-v0/track_a_06_report.json`
- `python scripts/validate_source_page_view_model.py`
- `python -m unittest tests.contracts.test_source_page_view_model`
- `git diff --check`
- `python scripts/validate_representation_contracts.py`
- `python scripts/validate_semantic_renderer_parity.py`
- `python scripts/validate_route_view_representation_matrix.py`
- `python scripts/validate_search_page_view_model.py`
- `python scripts/validate_object_page_view_model.py`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- required AIDE Lite checks

Full validation is recorded in:

- `control/audits/track-a-06-source-page-view-model-v0/validation.md`

Result:

- Hard validation lanes passed.
- AIDE verify and review-pack are WARN-only with zero errors because the active
  compact task packet still names TRACK-A-01 and optional review packet refs
  are missing.
