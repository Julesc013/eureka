# AIDE Latest Task Packet

## PHASE

historical-validator-drift-repair - SOURCE-FOUNDRY-PREVIEW-V0-HISTORICAL-VALIDATOR-DRIFT-REPAIR-02

## GOAL

Repair the remaining evidence-backed historical queue, validator, fixture, and obsolete-test drift that blocks a fresh Source Foundry Preview v0 external full-discovery rerun.

## WHY

The runtime leakage blocker is green, but repeated full-discovery failures still include stale historical queue and validator expectations. This task updates only validated historical checks and prepares one external rerun handoff after targeted lanes are green.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/SOURCE-FOUNDRY-PREVIEW-V0-HISTORICAL-VALIDATOR-DRIFT-REPAIR-02/task.yaml`
- `control/audits/validation/source_foundry_preview_v0_drift_triage/failure_inventory.json`
- `control/audits/validation/source_foundry_preview_v0_drift_triage/root_cause_groups.json`
- `control/audits/validation/source_foundry_preview_v0_drift_repair_01/UNRESOLVED_ITEMS.md`
- `control/audits/validation/source_foundry_runtime_leakage_repair_00/repair_report.json`
- `docs/operations/TEST_AND_EVAL_LANES.md`

## ALLOWED_PATHS

- `.aide/queue/SOURCE-FOUNDRY-PREVIEW-V0-HISTORICAL-VALIDATOR-DRIFT-REPAIR-02/**`
- `.aide/context/**`
- `control/audits/validation/source_foundry_preview_v0_historical_drift_repair_02/**`
- `docs/reference/validation/source_foundry_preview_v0_post_historical_repair_02/**`
- `docs/operations/TEST_AND_EVAL_LANES.md`
- `tests/operations/**`
- `tests/scripts/**`
- `scripts/validate_search_hunt_track.py`
- `scripts/validate_search_hunt_runtime.py`
- `scripts/validate_search_hunt_ui.py`
- `scripts/validate_search_hunt_commands.py`
- `scripts/validate_search_hunt_exhaustion.py`
- `scripts/validate_search_need_runtime.py`
- `scripts/validate_hunt_to_search_need.py`
- `scripts/validate_hunt_to_workunits.py`
- `scripts/validate_background_hunt_runner.py`
- `scripts/validate_hunt_remediation.py`
- `scripts/validate_hunt_remediation_continue.py`
- `scripts/validate_hunt_replay.py`
- `scripts/validate_agent_research_task_contract.py`
- `scripts/validate_ai_escalation_gate.py`
- `scripts/validate_local_appliance_track.py`
- `scripts/validate_local_instance_bootstrap.py`
- `scripts/validate_local_instance_migration_guard.py`
- `scripts/validate_local_http_service.py`
- `scripts/validate_local_runtime_composition.py`
- `scripts/validate_local_html_workbench.py`
- `scripts/validate_local_lan_safety_gate.py`
- `scripts/validate_local_lan_smoke.py`
- `scripts/validate_clean_machine_bootstrap.py`
- `scripts/validate_workunit_queue.py`
- `scripts/validate_local_worker_runner.py`
- `scripts/validate_local_review_rebuild.py`
- `scripts/validate_local_quarantine_staging_model.py`
- `scripts/validate_dev_to_main_promotion_03.py`
- `scripts/validate_dev_to_main_promotion_04.py`
- `scripts/validate_public_alpha_launch_defer.py`
- `scripts/validate_ia_readiness_polish.py`
- `scripts/validate_repo_structure_canon.py`
- `scripts/validate_repository_layout.py`
- `scripts/validate_runtime_architecture_leakage.py`
- `scripts/check_full_discovery.py`
- `scripts/eureka_test_select.py`
- `scripts/check_architecture_boundaries.py`
- `scripts/check_generated_artifact_cleanliness.py`
- `scripts/validate_public_alpha_readonly.py`
- `scripts/validate_snapshot_relay.py`
- `contracts/repo/root_allowlist.contract.toml`
- `control/inventory/tests/**`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `runtime/**`
- `contracts/**` except `contracts/repo/root_allowlist.contract.toml`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `source/provider implementations`
- `review stores and decisions`
- `reviewed-record materialization paths`
- `reviewed/master/public index stores`
- `snapshots/public projections`
- `Workbench runtime`
- `release/**`
- `archive/**`
- `LICENSE.md`
- `LICENSE-SUMMARY.md`
- `NOTICE.md`
- `README.md`
- `.aide/queue/index.yaml`
- public exposure, tunnel, hosting, or launch implementation

## IMPLEMENTATION

- Reproduce targeted lanes against current HEAD before patching.
- Repair only failures that still reproduce.
- Use explicit, narrow successor semantics requiring historical completion plus validated evidence.
- Reject fabricated or unrelated successor states.
- Replace obsolete staging absence assertions with safety assertions.
- Do not run full unittest discovery inside this AI session.

## VALIDATION

- `python scripts/validate_runtime_architecture_leakage.py --json`
- `python -m unittest tests.operations.test_legacy_runtime_leakage_remediation tests.operations.test_runtime_architecture_leakage -v`
- `python scripts/validate_local_worker_runner.py --json`
- `python -m unittest tests.operations.test_local_worker_scripts -v`
- HUNT targeted lane
- LOCAL targeted lane
- dev-to-main promotion validator lane
- repo-layout/canon lane
- `python scripts/validate_public_alpha_launch_defer.py --json`
- `python scripts/validate_ia_readiness_polish.py --json`
- `python -m unittest tests.operations.test_local_quarantine_staging_model -v`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_snapshot_relay.py`
- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `git diff --check`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py commit check --latest`

## NON_GOALS

- No full discovery inside AI.
- No runtime product behavior change.
- No queue-index change.
- No dev-to-main promotion.
- No public exposure, launch, production readiness, provider/network calls, downloads, Wayback replay, or license change.
- No reviewed records, reviewed/master mutation, public-index mutation, snapshot refresh, or review decision changes.
- No blanket skips, broad xfails, or arbitrary future queue acceptance.

## ACCEPTANCE

- Dedicated authority packet exists and `.aide/queue/index.yaml` is unchanged.
- Refreshed baseline records old failures that now pass and failures still requiring repair.
- Targeted historical lanes are green.
- Runtime leakage remains green.
- External full-discovery handoff is created only if targeted lanes are green.
- Main promotion remains blocked until the external rerun returns failures 0 and errors 0.

## EVIDENCE

- changed files
- refreshed baseline JSON and Markdown
- successor semantics report
- targeted validation matrix
- unresolved items report
- external full-discovery handoff only if targeted lanes are green
- compact command outputs and exit statuses
- no queue-index, runtime, truth, public exposure, or license changes

## OUTPUT_SCHEMA

Return the task-specific final report from the prompt with status, repo state, refreshed baseline, successor semantics, historical repairs, validation, safety, external rerun handoff, commits, blockers, and next action.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 6600
- approx_tokens: 1650
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
