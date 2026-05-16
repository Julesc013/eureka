# Validation Summary

## Pre-Sync

- `python scripts/check_git_task_state.py --mode start-task --task-id EUREKA-AIDE-STABLE-UPGRADE-01`: blocked by expected local-only multi-machine warnings: dirty tree from pre-existing native `obj/`, local `main` behind remote, local `dev` ahead/behind `origin/dev`, branch name not task id.
- Existing AIDE before sync: `doctor`, `validate`, `test`, `selftest`, `review-pack`, `commit check --latest`, `git policy` passed.
- Existing AIDE `verify`: warned on old active packet diff scope and pre-existing native `obj/`.
- `py -3 scripts/check_architecture_boundaries.py`: PASS.

## Post-Sync

- `py -3 -m py_compile .aide/scripts/aide_lite.py`: PASS.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py intent validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repo validate`: WARN, no failures; 5891 unknown classifications remain for Q56/Q57 refinement.
- `py -3 .aide/scripts/aide_lite.py quality validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py refactor validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py roots validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py tools validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py install validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py repair validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py upgrade validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py rollback validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py uninstall validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py changelog validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py github validate`: PASS after report-only advisory generation.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN; expected because active Q56 packet is narrower than the completed Q55 upgrade diff and the pre-existing native `obj/` is untracked.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS.
- `py -3 scripts/check_architecture_boundaries.py`: PASS, 692 Python files checked.
- `git diff --check`: PASS.
- `git check-ignore .aide.local/`: PASS, `.aide.local/` ignored.

## Eval

- `py -3 .aide/scripts/aide_lite.py eval list`: PASS, 136 active golden tasks.
- `py -3 .aide/scripts/aide_lite.py eval run`: abnormal exit `-1` after about 258 seconds with no captured output; recorded as a warning, not hidden.
- Targeted critical golden tasks passed after tightening the Q56 task packet:
  - `compact_task_packet_golden`: PASS.
  - `eureka_architecture_context_golden`: PASS.
  - `evidence_review_packet_golden`: PASS.
  - `generated_agent_guidance_golden`: PASS.
  - `no_secret_or_local_state_golden`: PASS.
  - `repo_boundary_golden`: PASS.
  - `tool_absorption_policy_golden`: PASS.
  - `tool_inventory_schema_golden`: PASS.
  - `tool_wrap_plan_schema_golden`: PASS.
  - `tools_no_execution_golden`: PASS.
  - `upgrade_preserves_target_state_golden`: PASS.
  - `install_preserves_target_state_golden`: PASS.

## Security / Local State

- Broad targeted scan returned policy/example/test matches only.
- High-confidence secret scan found no actual keys. Matches were test fixtures or policy text:
  - one fake `sk-` shaped fixture in `tests/scripts/test_validate_local_staging_manifest.py`;
  - two private-key marker test assertions/fixtures;
  - no `OPENAI_API_KEY=...`, `ANTHROPIC_API_KEY=...`, `DEEPSEEK_API_KEY=...`, or long assignment-shaped secret values.
