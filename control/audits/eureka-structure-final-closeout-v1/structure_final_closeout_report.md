# Eureka Structure Final Closeout v1

## Summary

This closeout grouped low-risk runtime, contract, and example taxonomy families, preserved runtime compatibility imports with shim packages, and classified remaining taxonomy/generated-artifact debt instead of hiding it. It did not intentionally change product behavior, source connector behavior, public search behavior, or live-source policy.

## Before/After Contracts First-Level Dirs

- Before: `actions, ai, api, archive, connectors, control_schemas, domain, evidence, evidence_ledger, explanation, extraction, gateway, hosting, identity, master_index, native, node, packs, pages, projections, query, relay, repo, representations, resolution_run, runtime, scout, search, search_interaction, search_quality, snapshots, source_cache, source_registry, source_sync, sources, stores, testing, ui, user_cost, view_models, views, workbench`
- After: `ai, api, archive, command, connectors, domain, evidence, explanation, extraction, gateway, hosting, identity, index, native, node, pack, query, relay, repo, representation, resolution, runtime, schema, scout, search, snapshots, source, stores, surface, testing, user_cost, view, workbench`

## Before/After Runtime First-Level Dirs

- Before: `actions, agent_research, ai_escalation, candidate_index, connectors, engine, evidence_ledger, extraction, extraction_safe_fixtures, gateway, hosting, local_appliance, local_eval, local_foundry, local_network, local_operator, local_review, local_service, local_worker, packs, pages, public_index, relay, resolution_run, review_queue, search_hunt, search_need, search_quality, snapshots, source_cache, source_observation, source_registry, workunit_queue`
- After: `actions, agent_research, ai_escalation, candidate_index, connectors, engine, evidence, evidence_ledger, extraction, extraction_safe_fixtures, gateway, hosting, index, local, local_appliance, local_eval, local_foundry, local_network, local_operator, local_review, local_service, local_worker, packs, pages, public_index, relay, resolution_run, review, review_queue, search, search_hunt, search_need, search_quality, snapshots, source, source_cache, source_observation, source_registry, worker, workunit_queue`

## Before/After Examples First-Level Dirs

- Before: `actions, ai_assisted_drafting, ai_providers, audits, candidate_index, candidate_promotion, candidate_promotion_dry_runs, candidates, commit_messages, comparison_pages, compatibility_aware_ranking, connectors, contribution_packs, demand_dashboard, design_tokens, domain, evidence_ledger, evidence_ledger_plans, evidence_ledger_records, evidence_packs, evidence_weighted_ranking, extraction, f0, hosting, ia_hunt_bridge, ia_live_metadata_lane, identity_resolution, import_reports, index_packs, internet_archive_metadata, known_absence_pages, local_foundry_state, local_staging_manifests, manual_observations, master_index_review_queue, native, node_policy_evaluations, nodes, object_pages, observation_candidates, observation_reviews, pack_builder, pack_drafts, pack_exports, pack_import_dry_run, pack_quarantine, page_runtime_dry_run, play, probe_queue, public_search_ranking_dry_run, query_guard, query_observations, query_result_cache, relay, renderer_parity, representations, resolution_run, result_merge, review_queue, review_queue_entries, reviewed_index, reviewed_public_index_rebuilds, reviewed_public_records, scout, search_miss_ledger, search_misses, search_need_seed_conversions, search_need_seeds, search_needs, search_quality, search_result_explanations, snapshots, source_cache, source_cache_plans, source_cache_records, source_cache_to_evidence, source_coverage, source_packs, source_pages, source_sync, sources, static_projections, syn, syn_foundation, view_models, work_unit_results, work_units, workbench, workunit_dry_runs, workunit_seed_conversions, workunit_seeds, workunits`
- After: `actions, ai_assisted_drafting, ai_providers, audits, commit_messages, comparison_pages, connectors, demand_dashboard, design_tokens, domain, evidence, extraction, f0, hosting, ia_hunt_bridge, ia_live_metadata_lane, identity_resolution, import_reports, index, internet_archive_metadata, known_absence_pages, local_foundry_state, local_staging_manifests, master_index_review_queue, native, node_policy_evaluations, nodes, object_pages, observation_candidates, packs, page_runtime_dry_run, play, probe_queue, relay, renderer_parity, representations, resolution_run, result_merge, review, scout, search, snapshots, sources, static_projections, syn, syn_foundation, view_models, work_units, workbench`

## Moved Paths

- Total moved path entries: `91`
- Runtime taxonomy moves: `19`
- Contract taxonomy moves: `24`
- Examples taxonomy moves: `48`

See `path_migration_map.json` and `control/inventory/repo_path_aliases.json`.

## Deleted Paths

- Deleted path count: `0`
- No tracked content was silently deleted. Old runtime import paths remain as compatibility shim packages where imports need continuity.

## Archived Paths

- Archived path count: `0`
- This closeout did not add new archive routing. Prior archive routing remains intact.

## Compatibility Shims/Wrappers

- Runtime compatibility shim count: `19`
- Script compatibility wrappers remain under `scripts/` and point to `tools/` implementations.

## Remaining Taxonomy Debt

- Remaining classified taxonomy debt count: `46`
- Remaining debt is recorded in `taxonomy_debt_after.json` and `control/policies/path_taxonomy_policy.json`.

## Generated Artifact Visibility

- Generated visibility status: `valid`
- Tracked `site/dist/` files: `58`
- Tracked `tmp/` files: `0`
- Tracked `/dist/` paths: `62`
- Tracked `/build/` paths: `4`
- Tracked `/coverage/` paths: `76`
- `.aide/export` is classified as artifact-only, `.aide/reports` as evidence-only, and `control/audits/**/generated` as audit evidence only.

## Validators Updated

- `tools/validators/validate_path_taxonomy.py` recognizes runtime compatibility-only first-level wrappers.
- `tools/validators/validate_taxonomy_closeout_policy.py` validates the final closeout evidence and canonical path policy.
- `tools/auditors/audit_generated_artifact_visibility.py` classifies source coverage fixture paths.
- Runtime/source/contract/example validators were updated to canonical moved paths.

## Docs Updated

- `docs/REPO_LAYOUT.md`
- `docs/architecture/PATH_TAXONOMY_CLOSEOUT.md`
- `runtime/README.md`
- `examples/README.md`

## Validation Commands and Statuses

| Command | Status |
| --- | --- |
| `git diff --check` | pass; line-ending warnings only |
| `python scripts/validate_repo_structure_canon.py --json` | pass |
| `python scripts/validate_repo_structure_canon.py --strict --json` | pass |
| `python scripts/check_architecture_boundaries.py` | pass |
| `python scripts/validate_path_taxonomy.py --json` | pass; classified debt count `46` |
| `python scripts/validate_taxonomy_closeout_policy.py --json` | pass |
| `python scripts/audit_generated_artifact_visibility.py --json` | pass |
| `python scripts/validate_contract_taxonomy.py` | pass |
| `python scripts/validate_public_static_site.py` | pass |
| `python scripts/validate_pack_set.py` | pass |
| `python scripts/eureka_test_select.py --changed --failed-first --json` | pass selector |
| `python scripts/eureka_test_select.py --promotion --json` | pass selector; full discovery required |
| `python scripts/validate_source_observation_seam.py --json` | pass |
| `python scripts/validate_local_runtime_composition.py --json` | pass |
| `python scripts/validate_contract_taxonomy_plan.py --json` | pass after UI contract path remediation |
| `python scripts/validate_local_http_service.py --json` | pass after canonical local appliance import allowlist update |
| Focused moved-path unittest lanes | pass |
| `python -m unittest discover -s tests -t .` | pass; `4914` tests in `2660.506s` |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | pass; no generated drift, no network, no model provider use, no site/dist mutation |

## Failures Remediated

- Repaired stale references created by moving runtime, contract, and example families.
- Recomputed affected example pack checksums.
- Rebuilt the committed public static search index after path updates.
- Moved `contracts/runtime/source_observation.v0.json` to `contracts/runtime/source/observation.v0.json` to match its governed contract id and inventory references.
- Moved three surface UI contract files to the nested canonical paths already recorded in the contract taxonomy inventory.
- Updated two ranking validator tests that still referenced the old `examples/evidence_weighted_ranking` path.
- Updated the LOCAL-04 validator allowlist for canonical `runtime.local.appliance` imports.
- Updated audit manifests that validators read so they no longer point at removed example paths.
- Classified `examples/sources/coverage/` generated-looking fixtures in the generated visibility auditor.
- Reran full unittest discovery after remediation; the clean-tree run passed.

## Known Remaining Debt

- Contracts: `ai, explanation, extraction, node, scout, user_cost`
- Runtime: `actions, agent_research, ai_escalation, extraction_safe_fixtures`
- Examples: `actions, ai_assisted_drafting, ai_providers, audits, commit_messages, comparison_pages, demand_dashboard, design_tokens, domain, extraction, f0, hosting, ia_hunt_bridge, ia_live_metadata_lane, identity_resolution, internet_archive_metadata, known_absence_pages, local_foundry_state, local_staging_manifests, master_index_review_queue, node_policy_evaluations, nodes, object_pages, observation_candidates, page_runtime_dry_run, play, probe_queue, renderer_parity, representations, resolution_run, result_merge, scout, static_projections, syn, syn_foundation, view_models`

## Explicit Non-Claims

- No intentional product behavior change.
- No intentional source connector behavior change.
- No intentional public search behavior change.
- No intentional live-source behavior change.
- No production-readiness claim.
- No generated output is treated as source truth.
