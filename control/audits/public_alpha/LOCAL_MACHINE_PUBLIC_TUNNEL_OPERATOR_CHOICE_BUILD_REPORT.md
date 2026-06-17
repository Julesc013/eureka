# Local Machine Public Tunnel Operator Choice Build Report

Task: `LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-CHOICE-00`

Status: `PASS_WITH_WARNINGS`

## Repo State

- Branch: `dev`
- HEAD at task start: `8ca08ffa5ce9f1ba7c811e81d2dd4a68c6456d5d`
- Worktree at task start: clean
- `HEAD...origin/dev` at task start: ahead 0, behind 0
- Queue recommendation: `IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00`
- Selected launch-track task: `LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-CHOICE-00`

After this task is committed, local `dev` is expected to be ahead of
`origin/dev` by this commit until pushed. Do not start public exposure rehearsal
from an unpushed local state without explicitly recording that decision.

## Operator Choice

- Exposure mode: `reverse_tunnel`
- Provider class: `provider_managed_https_tunnel`
- Provider name: `OPERATOR_REQUIRED`
- Public URL: `OPERATOR_REQUIRED`
- Public URL status: `operator_required`
- TLS/provider HTTPS: `operator_required`
- Ops posture: `READY_FOR_EXPOSURE_PLAN`
- Exposure plan: `READY_FOR_OPERATOR_URL`
- Choice status: `BLOCKED_ON_OPERATOR_PROVIDER_URL`

## Commands Added Or Confirmed

```powershell
python scripts/eureka_local_machine_public_exposure.py choose --plan .eureka/public-alpha/exposure/latest/exposure_plan.json --ops-posture .eureka/ops/public-alpha/latest/ops_posture.json --mode reverse_tunnel --provider-class provider_managed_https_tunnel --provider-name OPERATOR_REQUIRED --public-url OPERATOR_REQUIRED --out .eureka/public-alpha/exposure/operator-choice/latest
```

```powershell
python scripts/eureka_local_machine_public_exposure.py validate-choice --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json --strict
```

```powershell
python scripts/eureka_local_machine_public_exposure.py choice-status --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json
```

```powershell
python scripts/eureka_local_machine_public_exposure.py choice-report --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json
```

## Artifacts Generated

- `.eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json`
- `.eureka/public-alpha/exposure/operator-choice/latest/OPERATOR_CHOICE_REPORT.md`
- `control/audits/public_alpha/LOCAL_MACHINE_PUBLIC_TUNNEL_OPERATOR_CHOICE_STATE.json`
- `control/audits/public_alpha/LOCAL_MACHINE_PUBLIC_TUNNEL_OPERATOR_CHOICE_STATE.md`
- `control/audits/public_alpha/LOCAL_MACHINE_PUBLIC_TUNNEL_OPERATOR_CHOICE_REPORT.json`
- `control/audits/public_alpha/LOCAL_MACHINE_PUBLIC_TUNNEL_OPERATOR_CHOICE_REPORT.md`
- `control/audits/public_alpha/LOCAL_MACHINE_PUBLIC_TUNNEL_OPERATOR_CHOICE_BUILD_REPORT.json`
- `control/audits/public_alpha/LOCAL_MACHINE_PUBLIC_TUNNEL_OPERATOR_CHOICE_BUILD_REPORT.md`

## Validation

- `python scripts/eureka_public_alpha_ops_posture.py validate --plan .eureka/ops/public-alpha/latest/ops_posture.json --strict`: PASS
- `python scripts/eureka_local_machine_public_exposure.py validate --plan .eureka/public-alpha/exposure/latest/exposure_plan.json --strict`: PASS
- `python scripts/eureka_local_machine_public_exposure.py choose --plan .eureka/public-alpha/exposure/latest/exposure_plan.json --ops-posture .eureka/ops/public-alpha/latest/ops_posture.json --mode reverse_tunnel --provider-class provider_managed_https_tunnel --provider-name OPERATOR_REQUIRED --public-url OPERATOR_REQUIRED --out .eureka/public-alpha/exposure/operator-choice/latest`: PASS
- `python scripts/eureka_local_machine_public_exposure.py validate-choice --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json --strict`: PASS
- `python scripts/eureka_local_machine_public_exposure.py choice-status --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json`: PASS
- `python scripts/eureka_local_machine_public_exposure.py choice-report --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json`: PASS
- `python -m unittest tests.operations.test_local_machine_public_tunnel_operator_choice`: PASS, 11 tests
- `python scripts/check_architecture_boundaries.py`: PASS
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: expected pre-commit warning; new tracked `control/audits/public_alpha` operator-choice reports were flagged as generated drift before commit. Rerun after commit is required.

Skipped:

- Full unittest discovery: promotion/nightly/manual gate, not selected for this task.
- Server/tunnel/proxy smoke: forbidden by this plan-only task.

## Safety Confirmation

- Public exposure enabled: false
- Tunnel/proxy started: false
- Server started: false
- DNS modified: false
- Firewall/router modified: false
- Public mutation: false
- Workbench exposure: false
- Live metadata: false
- Downloads/uploads: false / false
- Launch approval: false
- Production readiness claim: false

## Remaining Launch Blockers

- Operator must choose a real tunnel/proxy provider.
- Operator must supply a real HTTPS public URL.
- Provider HTTPS/TLS posture must be validated.
- Staged record ID is needed for future `/record` route smoke.
- Actual tunnel/proxy rehearsal has not run.
- Full discovery launch report is missing.
- Release promotion report is missing.
- Manual public launch approval is missing.
- Final public launch has not happened.

## Protected Path Impact

- `docs/canon/`: not touched
- `contracts/`: not touched
- Runtime product behavior: not changed; only exposure-planning runtime was extended
- `.aide/queue/`: not touched
- `release/`: not touched
- Archive zips: not touched
- Public network exposure: not enabled

## Recommended Next Task

```text
LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-INPUT-00
```
