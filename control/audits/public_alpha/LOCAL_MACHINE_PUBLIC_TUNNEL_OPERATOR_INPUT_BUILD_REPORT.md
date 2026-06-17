# Local Machine Public Tunnel Operator Input Build Report

Task: `LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-INPUT-00`

Status: `PASS_WITH_WARNINGS`

## Summary

The existing operator-choice machinery was reused. The generated `.eureka`
operator-choice artifact records a safe blocked state because no real provider
name or HTTPS public URL was supplied.

Focused validation passed. The only validation warning was the expected
pre-commit generated-artifact cleanliness failure caused by the new
`audit_generated` files being uncommitted at the time of the check.

## Commands Run So Far

```powershell
python scripts/check_git_task_state.py --mode start-task --task-id LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-INPUT-00
```

Result: `WARN`

Only `task_id_branch_name_match` warned. The branch is `dev`.

```powershell
git fetch origin
git status --short
git branch --show-current
git rev-parse HEAD
git rev-list --left-right --count origin/dev...HEAD
```

Result: `PASS`

- Branch: `dev`
- HEAD: `4d882a8add09aea79e11b979ab97414610a71a97`
- `origin/dev...HEAD`: `0 0`
- Short status: clean

```powershell
python scripts/eureka_public_alpha_ops_posture.py validate --plan .eureka/ops/public-alpha/latest/ops_posture.json --strict
```

Result: `PASS`

- Status: `READY_FOR_EXPOSURE_PLAN`
- Launch blockers remain.

```powershell
python scripts/eureka_local_machine_public_exposure.py validate --plan .eureka/public-alpha/exposure/latest/exposure_plan.json --strict
```

Result: `PASS`

- Status: `READY_FOR_OPERATOR_URL`
- Seven blockers remain.

```powershell
python scripts/eureka_local_machine_public_exposure.py choose --plan .eureka/public-alpha/exposure/latest/exposure_plan.json --ops-posture .eureka/ops/public-alpha/latest/ops_posture.json --mode reverse_tunnel --provider-class provider_managed_https_tunnel --provider-name OPERATOR_REQUIRED --public-url OPERATOR_REQUIRED --staged-record-id local-reviewed-record:1792f5ba3d54774c --out .eureka/public-alpha/exposure/operator-choice/latest
```

Result: `PASS`

- Generated: `.eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json`
- Status: `BLOCKED_ON_OPERATOR_PROVIDER_URL`
- Remote sync status: synced
- Public exposure enabled: false

```powershell
python scripts/eureka_local_machine_public_exposure.py validate-choice --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json --strict
python scripts/eureka_local_machine_public_exposure.py choice-status --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json
```

Result: `PASS`

- Safe: true
- Provider name: `OPERATOR_REQUIRED`
- Public URL status: `operator_required`
- Provider HTTPS status: `operator_required`
- Staged record ID status: present
- Next task from generated choice: `LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-INPUT-00`

## Focused Validation

```powershell
python -m json.tool control/audits/public_alpha/LOCAL_MACHINE_PUBLIC_TUNNEL_OPERATOR_INPUT_STATE.json
python -m json.tool control/audits/public_alpha/LOCAL_MACHINE_PUBLIC_TUNNEL_OPERATOR_INPUT_REPORT.json
python -m json.tool control/audits/public_alpha/LOCAL_MACHINE_PUBLIC_TUNNEL_OPERATOR_INPUT_BUILD_REPORT.json
```

Result: `PASS`

```powershell
python -m unittest tests.operations.test_local_machine_public_tunnel_operator_choice
```

Result: `PASS`

- Ran 11 tests.

```powershell
git diff --check
```

Result: `PASS`

```powershell
python scripts/check_architecture_boundaries.py
```

Result: `PASS`

- Checked 934 Python files.
- No architecture-boundary violations found.

```powershell
python scripts/check_generated_artifact_cleanliness.py --check --json
```

Result: `WARN_PRE_COMMIT_DRIFT`

The check failed before commit only because the newly added
`control/audits/public_alpha/LOCAL_MACHINE_PUBLIC_TUNNEL_OPERATOR_INPUT_*`
audit files were uncommitted `audit_generated` files. Rerun after commit is
required.

```powershell
python scripts/validate_public_alpha_readonly.py
```

Result: `PASS`

```powershell
python scripts/public_alpha_smoke.py --json
```

Result: `PASS`

- 18 checks passed.
- 0 checks failed.

```powershell
python scripts/validate_snapshot_relay.py
python scripts/validate_public_alpha_hosting_readiness.py
python scripts/validate_public_alpha_launch_candidate.py
```

Result: `PASS`

- Snapshot relay validation: pass.
- Public alpha hosting readiness validation: valid.
- Public alpha launch candidate validation: pass.

## Warnings

- Provider name and public URL remain `OPERATOR_REQUIRED`.
- Provider HTTPS/TLS posture remains unvalidated.
- Generated-artifact cleanliness must be rerun after commit.

## Non-Claims

- AIDE was not run for this audit.
- Full unittest discovery was not run and is not claimed.
- No tunnel/proxy, public exposure, release promotion, or launch approval was performed.
