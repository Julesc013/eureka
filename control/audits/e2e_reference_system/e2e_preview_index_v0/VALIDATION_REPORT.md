# Validation Report

Status: `PASS_WITH_WARNINGS`

Focused lanes passed:

- `python -m unittest tests.search.test_e2e_preview_index tests.e2e.test_e2e_preview_index tests.e2e.test_local_search_preview_index -v`
- `python -m unittest tests.e2e.test_local_search_index_builder tests.e2e.test_local_search_server tests.e2e.test_local_search_p0_no_mutation -v`
- `python -m unittest tests.operations.test_ia_source_observation_cache_delta tests.operations.test_ia_candidate_index_refresh tests.operations.test_ia_evidence_ledger_summary -v`
- `python -m unittest tests.runtime.test_e2e_reference_runner tests.e2e.test_e2e_reference_runner -v`
- Preview CLI build/validate/stats/search smoke over local generated source-wave material.
- `python scripts/check_architecture_boundaries.py`
- `python scripts/validate_runtime_architecture_leakage.py --json`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_snapshot_relay.py`
- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `python scripts/validate_contract_taxonomy.py`
- `python scripts/validate_repo_structure_canon.py`
- `python -m unittest tests.operations.test_contract_taxonomy tests.operations.test_repo_structure_canon -v`
- `python scripts/validate_test_lane_policy.py`
- `python -m unittest tests.operations.test_test_lane_policy tests.scripts.test_eureka_test_select tests.scripts.test_validate_test_lane_policy -v`
- `git diff --check`

## Warnings

- Full unittest discovery was not run or claimed; it remains a promotion/manual
  gate.
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
  failed before commit because the new tracked preview audit packet was still
  untracked. This is expected in the repo convention and must pass after commit.

## Preview Build Evidence

- Real local generated input build passed with 494 preview records.
- Strict validation passed with 0 errors.
- `reviewed_count`: 0.
- `reviewed_master_mutation`: false.
- `public_index_mutation`: false.
- `source_provider_calls`: false.
- `accepted_truth_creation`: false.
