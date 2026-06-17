# Local Machine Public Tunnel Plan Build Report

Task: `LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00`

Status: `PASS_WITH_WARNINGS`

## Repo State

- Branch: `dev`
- HEAD: `484a1001fbb7b6ea4293c1787a71bffdb97c9de6`
- Worktree: dirty during implementation; clean before task edits
- `HEAD...origin/dev`: ahead 0, behind 0
- Post-commit note: after this task is committed, local `dev` is expected to be
  ahead of `origin/dev` by this commit until pushed.
- Current queue recommendation: `IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00`
- Selected launch-track task: `LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00`

## Exposure Plan

- Selected mode: `reverse_tunnel`
- Public URL status: missing
- TLS/provider HTTPS status: missing
- Ops posture status: `READY_FOR_EXPOSURE_PLAN`
- Generated plan: `.eureka/public-alpha/exposure/latest/exposure_plan.json`
- Generated report: `.eureka/public-alpha/exposure/latest/EXPOSURE_PLAN_REPORT.md`
- Plan status: `READY_FOR_OPERATOR_URL`

## Commands Added Or Confirmed

```powershell
python scripts/eureka_local_machine_public_exposure.py plan --mode reverse_tunnel --ops-posture .eureka/ops/public-alpha/latest/ops_posture.json --out .eureka/public-alpha/exposure/latest
python scripts/eureka_local_machine_public_exposure.py validate --plan .eureka/public-alpha/exposure/latest/exposure_plan.json --strict
python scripts/eureka_local_machine_public_exposure.py status --plan .eureka/public-alpha/exposure/latest/exposure_plan.json
python scripts/eureka_local_machine_public_exposure.py report --plan .eureka/public-alpha/exposure/latest/exposure_plan.json
```

## Validation

- `python scripts/eureka_public_alpha_ops_posture.py validate --plan .eureka/ops/public-alpha/latest/ops_posture.json --strict`: PASS
- `python scripts/eureka_local_machine_public_exposure.py plan --mode reverse_tunnel --ops-posture .eureka/ops/public-alpha/latest/ops_posture.json --out .eureka/public-alpha/exposure/latest`: PASS
- `python scripts/eureka_local_machine_public_exposure.py validate --plan .eureka/public-alpha/exposure/latest/exposure_plan.json --strict`: PASS
- `python scripts/eureka_local_machine_public_exposure.py status --plan .eureka/public-alpha/exposure/latest/exposure_plan.json`: PASS
- `python -m unittest tests.operations.test_local_machine_public_tunnel_plan`: PASS, 10 tests
- `python -m unittest tests.e2e.test_local_machine_public_exposure_plan`: PASS, 6 tests
- `git diff --check`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS
- `python scripts/eureka_test_select.py --changed --failed-first --json`: PASS; full discovery not selected
- `python scripts/validate_test_lane_policy.py`: PASS
- `python -m unittest tests.scripts.test_eureka_test_select`: PASS, 3 tests
- `python -m unittest tests.operations.test_test_lane_policy`: PASS, 1 test
- `python -m unittest tests.scripts.test_validate_test_lane_policy`: PASS, 2 tests
- `python -m pytest tests/operations/test_local_machine_public_tunnel_plan.py`: SKIPPED, `pytest` is not installed
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: PRE-COMMIT WARNING because requested `control/audits/public_alpha` files are uncommitted audit-generated drift; rerun after commit required

## Remaining Launch Blockers

- Operator public URL/provider choice is missing.
- Provider HTTPS/TLS posture is missing.
- Known staged record ID is needed for future `/record` smoke.
- Tunnel/proxy rehearsal has not run.
- Full discovery launch report is missing.
- Release promotion report is missing.
- Manual public launch approval is missing.

## No-Public-Exposure Confirmation

- Public exposure enabled: false
- Server started: false
- Tunnel started: false
- Proxy started: false
- DNS modified: false
- Firewall/router modified: false
- Launch claimed: false

## Protected Path Impact

- `docs/canon/**`: not touched
- `contracts/**`: not touched
- Runtime search behavior: not touched
- `.aide/queue/**`: not touched
- Release artifacts: not touched
- Archive zips: not touched
- Public network exposure: not enabled

## Recommended Next Task

```text
LOCAL-MACHINE-PUBLIC-TUNNEL-OPERATOR-CHOICE-00
```
