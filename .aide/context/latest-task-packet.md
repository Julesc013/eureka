# AIDE Latest Task Packet

## PHASE

PUBLIC-SEARCH-UX-MODEL-00 - canonical public search view models

## GOAL

Define canonical public search UX view models so public web, Workbench, API/JSON,
classic HTML, text, and future agents render the same result-state semantics.

## WHY

Public alpha is structurally present but reviewed-record poor. The product needs
a search-first UX model that makes verified, candidate, need, absence, and source
lead states impossible to confuse while active discovery continues.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/public_alpha_reassess_result.json`
- `examples/snapshots/refresh/reviewed_record_section.json`
- `examples/snapshots/refresh/candidate_section_frontier_media.json`
- `examples/snapshots/refresh/candidate_section_legacy_software.json`
- `examples/snapshots/refresh/need_absence_section.json`

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-SEARCH-UX-MODEL-00/**`
- `.aide/queue/PUBLIC-SEARCH-UX-MVP-00/**`
- `.aide/queue/PUBLIC-SEARCH-UX-GATE-00/**`
- `.aide/queue/LIVE-METADATA-PILOT-BATCH-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `contracts/view/models/public_search/**`
- `runtime/public_alpha/search_ux_models.py`
- `runtime/public_alpha/__init__.py`
- `scripts/eureka_public_search_ux_model.py`
- `scripts/validate_public_search_ux_model.py`
- `tests/runtime/test_public_search_*.py`
- `tests/operations/test_public_search_ux_model_scripts.py`
- `tests/scripts/test_validate_public_search_ux_model.py`
- `examples/view_models/public_search/**`
- `control/policies/public_search_ux_model_policy.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_search_ux_model*.json`
- `control/audits/public-search-ux-model-00-v0/**`
- `docs/architecture/PUBLIC_SEARCH_UX_MODEL.md`
- `docs/operations/PUBLIC_SEARCH_UX_MODEL_RUNBOOK.md`
- `docs/reference/PUBLIC_SEARCH_VIEW_MODELS.md`
- `docs/reference/PUBLIC_SEARCH_RESULT_CARD_VIEW_MODEL.md`

## FORBIDDEN_PATHS

- duplicate contracts views root
- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `../eureka-test-runs/**`
- `secrets/**`
- `.env`
- private local files
- committed operator tokens
- provider credentials
- raw live source responses
- raw IA responses
- raw full-discovery stdout/stderr logs
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Extend the existing `contracts/view/models` authority.
- Add canonical public search result-card and page view-model contracts.
- Add deterministic runtime builders over snapshot-refresh examples.
- Add projection helpers for public web, operator Workbench, API JSON,
  classic HTML, and text.
- Add examples, docs, validator, tests, queue evidence, and audit evidence.

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_search_ux_model.py`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_snapshot_refresh.py`
- `python scripts/validate_candidate_index_runtime.py`
- `python scripts/validate_review_batch.py`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- focused public search UX model unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit
  check when practical

Full unittest discovery is not run by policy.

## COMMITS

Use repo-policy-compliant equivalent of:

```text
feat(public): add search UX view models
```

## EVIDENCE

- `control/inventory/public_search_ux_model_result.json`
- `control/inventory/public_search_ux_model_boundary_report.json`
- `control/audits/public-search-ux-model-00-v0/`
- `examples/view_models/public_search/search_page_view_model.json`

## NON_GOALS

- No public page redesign.
- No deployment, publish, or launch/readiness claim.
- No public mutation or public live source fanout.
- No downloads, extraction, model/provider calls, source probes, or live source calls.
- No reviewed/master/public index mutation.
- No accepted truth creation.

## ACCEPTANCE

- Result card statuses include verified, candidate, near_miss, known_need,
  absence, and source_lead.
- Candidate-like cards are review-required and not accepted truth.
- Public/API/classic/text projections are read-only.
- Agents can consume JSON packets without scraping HTML.
- Existing contract authority is extended; duplicate contracts views root is
  not created.
- Recommended next task remains `LIVE-METADATA-PILOT-BATCH-00`.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `PUBLIC_SEARCH_UX_MODEL`, `VALIDATION`,
`BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 1100
- budget_status: PASS
