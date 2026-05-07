# TRACK-A-04 Changed Files

## Contract Bundle

- `contracts/views/search_page.v0.json`
- `docs/reference/SEARCH_PAGE_VIEW_MODEL_CONTRACT.md`
- `control/inventory/publication/search_page_view_model_policy.json`
- `examples/view_models/search_page/minimal_search_page_v0.json`
- `examples/view_models/search_page/empty_search_page_v0.json`
- `examples/view_models/search_page/absence_search_page_v0.json`
- `examples/view_models/search_page/result_card_search_page_v0.json`
- `scripts/validate_search_page_view_model.py`
- `tests/contracts/test_search_page_view_model.py`
- `control/audits/track-a-04-search-page-view-model-v0/README.md`
- `control/audits/track-a-04-search-page-view-model-v0/track_a_04_report.json`
- `control/audits/track-a-04-search-page-view-model-v0/validation.md`

## Narrow Doc Pointer

- `docs/roadmap/TRACK_EXECUTION_PLAN.md`

The roadmap update only advances the Track A next-task pointer after A-04.

## AIDE Evidence

- `.aide/queue/TRACK-A-04/task.yaml`
- `.aide/queue/TRACK-A-04/status.yaml`
- `.aide/queue/TRACK-A-04/evidence/changed-files.md`
- `.aide/queue/TRACK-A-04/evidence/validation.md`
- `.aide/queue/TRACK-A-04/evidence/track-a-contract-result.md`
- `.aide/queue/TRACK-A-04/evidence/remaining-risks.md`
- `.aide/context/latest-review-packet.md`
- `.aide/evals/runs/latest-golden-tasks.json`
- `.aide/evals/runs/latest-golden-tasks.md`

## AIDE Tooling Alignment

- `.aide/policies/commit-messages.yaml`
- `.aide/reports/eureka-commit-message-standard.md`
- `.aide/scripts/aide_lite.py`

The commit-message checker now accepts the required Track A `contracts(...)`
subject type.
