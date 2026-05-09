# Validation

## Git Checks

- `git status --short` - PASS before merge and after merge commit; modified files are expected validation/audit cleanup before the audit commit.
- `git rev-parse -q --verify MERGE_HEAD` - PASS, absent after merge commit.
- `git fetch --all --tags` - PASS.
- `git diff --check` - PASS.
- `git grep -n -E "^(<<<<<<<|>>>>>>>)"` - PASS, no opening or closing conflict markers.
- `python scripts/check_architecture_boundaries.py` - PASS, 493 Python files checked and no architecture-boundary violations found.
- local `main` fast-forward to unified branch - PASS.
- first normal `git push origin main` - PASS, `f83b005..7a3d112`.

## Targeted Validators

- `python scripts/validate_track_a_contracts.py` - PASS.
- `python scripts/validate_agent_assisted_observation_policy.py` - PASS.
- `python scripts/validate_observation_candidate.py` - PASS.
- `python scripts/validate_observation_candidate_review_queue.py` - PASS.
- `python scripts/validate_search_need_seed_candidates.py` - PASS.
- `python scripts/validate_workunit_seed_candidates.py` - PASS.
- `python scripts/validate_obs_track_b_synchronization.py` - PASS.
- `python scripts/validate_obs_human_review_packet.py` - PASS.
- `python scripts/validate_eureka_node_manifest.py` - PASS.
- `python scripts/validate_eureka_node_policy.py` - PASS.
- `python scripts/validate_eureka_node_capability.py` - PASS.
- `python scripts/validate_eureka_workunit.py` - PASS.
- `python scripts/validate_eureka_workunit_result.py` - PASS.
- `python scripts/validate_local_foundry_state.py` - PASS.
- `python scripts/validate_query_observation_runtime.py` - PASS.
- `python scripts/validate_search_miss_ledger_runtime.py` - PASS.
- `python scripts/validate_search_need_runtime.py` - PASS.
- `python scripts/validate_workunit_dry_run_runner.py` - PASS.
- `python scripts/validate_node_policy_evaluator.py` - PASS.
- `python scripts/validate_candidate_store_runtime.py` - PASS.
- `python scripts/validate_local_source_cache_runtime_plan.py` - PASS.
- `python scripts/validate_local_evidence_ledger_runtime_plan.py` - PASS.
- `python scripts/validate_local_source_cache_runtime.py` - PASS.
- `python scripts/validate_local_evidence_ledger_runtime.py` - PASS.
- `python scripts/validate_source_cache_to_evidence_bridge.py` - PASS.
- `python scripts/validate_local_review_queue_runtime.py` - PASS.
- `python scripts/validate_candidate_promotion_dry_run.py` - PASS.
- `python scripts/validate_reviewed_public_index_rebuild_contract.py` - PASS.
- `python scripts/validate_pack_builder_runtime.py` - PASS.
- `python scripts/validate_pack_export_runtime.py` - PASS.
- `python scripts/audit_track_b_integration.py --check` - PASS with documented warnings and zero critical blockers.

## Generated Artifact and Tests

- `python scripts/generate_public_alpha_rehearsal_evidence.py --check` - PASS after refresh.
- `python scripts/generate_public_alpha_rehearsal_evidence.py --update` - PASS after switching to local `main` to refresh branch metadata.
- `python scripts/check_generated_artifact_drift.py --json` - PASS.
- `python -m unittest tests.hardening.test_external_baseline_guards.ExternalBaselineGuardsTest.test_scripts_and_docs_do_not_claim_google_or_archive_scraping` - PASS after sentinel rewrite.
- `python -m unittest discover -s tests -t .` - PASS, 2494 tests.

## AIDE Lite

- `py -3 .aide/scripts/aide_lite.py doctor` - PASS.
- `py -3 .aide/scripts/aide_lite.py validate` - PASS.
- `py -3 .aide/scripts/aide_lite.py test` - PASS.
- `py -3 .aide/scripts/aide_lite.py selftest` - PASS.
- `py -3 .aide/scripts/aide_lite.py verify` - WARN, zero errors.
- `py -3 .aide/scripts/aide_lite.py eval list` - PASS.
- `py -3 .aide/scripts/aide_lite.py eval run` - PASS.
- `py -3 .aide/scripts/aide_lite.py review-pack` - PASS.
- `py -3 .aide/scripts/aide_lite.py adapter validate` - PASS.
