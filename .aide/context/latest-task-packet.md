# AIDE Latest Task Packet

phase: INSTANCE-LAYOUT-01

## PHASE

INSTANCE-LAYOUT-01

## GOAL

Standardize the sibling `instances/default` layout for local appliance runtime state.

## WHY

Eureka source code and mutable operator-owned runtime state must remain separate. The preferred local development layout should be `workspace_root/eureka` for the repo and `workspace_root/instances/default` for daily local state, while the legacy sibling `workspace_root/eureka-instance` remains accepted only as an explicit legacy path.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/context/latest-context-packet.md`
- `control/inventory/instance_layout_preflight_result.json`
- `control/inventory/instance_layout_preflight_diff_classification.json`
- `control/audits/instance-layout-preflight-01-v0/`
- `docs/operations/LOCAL_INSTANCE_LAYOUT.md`
- `docs/operations/INSTANCE_PATH_POLICY.md`

## ALLOWED_PATHS

- `docs/operations/LOCAL_INSTANCE_LAYOUT.md`
- `docs/operations/INSTANCE_PATH_POLICY.md`
- `docs/operations/LOCAL_HTTP_SERVICE_RUNBOOK.md`
- `docs/operations/LOCAL_HTML_WORKBENCH_RUNBOOK.md`
- `docs/operations/SEARCH_HUNT_RUNTIME_RUNBOOK.md`
- `docs/operations/SEARCH_HUNT_COMMAND_RUNBOOK.md`
- `docs/operations/LOCAL_APPLIANCE_TRACK.md`
- `runtime/local_appliance/paths.py`
- `runtime/local_appliance/manifest.py`
- `runtime/local_appliance/validation.py`
- `runtime/local_appliance/status.py`
- `runtime/local_appliance/composition.py`
- `scripts/eureka_resolve_paths.py`
- `scripts/eureka_new_instance.py`
- `scripts/eureka_list_instances.py`
- `scripts/eureka_migrate_instance_layout.py`
- `scripts/eureka_init_instance.py`
- `scripts/eureka_validate_instance.py`
- `scripts/eureka_instance_status.py`
- `scripts/eureka_local_runtime_status.py`
- `scripts/validate_instance_layout_policy.py`
- `tests/runtime/test_local_appliance_paths.py`
- `tests/operations/test_instance_layout_policy.py`
- `tests/operations/test_instance_layout_scripts.py`
- `control/policies/instance_layout_policy.json`
- `control/inventory/instance_layout_current_policy.json`
- `control/inventory/instance_layout_migration_plan.json`
- `control/inventory/instance_layout_result.json`
- `control/inventory/instance_layout_next_task_decision.json`
- `.aide/queue/INSTANCE-LAYOUT-01/task.yaml`
- `.aide/queue/PLAY-00/task.yaml`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `control/audits/instance-layout-01-v0/**`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- `instances/**`
- private local files
- committed operator tokens
- committed provider credentials
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Add governed instance layout policy and shared path resolver.
- Keep explicit `--instance` paths as the command boundary.
- Add dry-run migration/list/new-instance helpers without moving operator data automatically.
- Update runbooks, validator, tests, inventories, audit evidence, and queue handoff.

## VALIDATION

- `git status --short`
- `git diff --check`
- JSON validation for INSTANCE-LAYOUT inventories and audit report
- `python scripts/eureka_resolve_paths.py --json`
- `python scripts/eureka_list_instances.py --json`
- `python scripts/eureka_migrate_instance_layout.py --from ../eureka-instance --to ../instances/default --dry-run --json`
- `python scripts/validate_instance_layout_policy.py`
- focused instance-layout tests
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- full unittest discovery when practical
- AIDE doctor, validate, test, selftest, verify, and review-pack

## EVIDENCE

- `.aide/queue/INSTANCE-LAYOUT-01/`
- `control/inventory/instance_layout_result.json`
- `control/audits/instance-layout-01-v0/`

## NON_GOALS

No source probes, Internet Archive calls, extraction, AI/model/provider calls, downloads, install/execute behavior, deployment, public launch claim, production readiness claim, master-index mutation, reviewed-index semantic mutation, automatic deletion of `D:\Projects\Eureka\eureka-instance`, automatic filesystem move outside the repo, or live source/search behavior changes.

## ACCEPTANCE

- Preferred local dev layout is documented as sibling `instances/default`.
- Existing sibling `eureka-instance` remains supported as an explicit legacy path.
- Repo-nested `eureka-instance` is no longer the documented default.
- Shared path resolver, CLI helpers, validator, tests, inventories, audit evidence, and next-task handoff exist.
- No operator instance is moved or deleted and no instance state is committed.

## OUTPUT_SCHEMA

- `control/inventory/instance_layout_result.json` uses `instance_layout_result.v0`.
- `control/inventory/instance_layout_next_task_decision.json` uses `instance_layout_next_task_decision.v0`.

## TOKEN_ESTIMATE

approx_tokens: 1450
