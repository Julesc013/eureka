# Dev To Main Promotion Build Report

Task: `DEV-TO-MAIN-PROMOTION-READINESS-AND-SYNC-00`

Status: `PENDING_POST_PROMOTION_VERIFICATION`

## Branch Before

- Branch: `dev`
- Dev commit before promotion reports:
  `f523e3eccafcf2ccf02493d93e9ebee5ebcb3f78`
- Main commit before:
  `339b61d14d01e923fd87931523d849e4f26cf2ec`
- `origin/main...origin/dev`: `0 131`
- Main-only commits: none
- Unsafe divergence: none

## Promotion Decision

```text
PROMOTE_DEV_TO_MAIN
```

The selected method is direct fast-forward branch sync:

```powershell
git push origin dev
git push origin dev:main
```

This report is written before the push so it can be included in the promoted
baseline. Post-promotion verification updates the final task result.

## Validation Before Promotion

- `python -m unittest tests.docs.test_public_docs -v`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- `git diff --check`: PASS
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: PASS
- `python scripts/validate_public_alpha_readonly.py`: PASS
- `python scripts/validate_snapshot_relay.py`: PASS
- `python scripts/validate_public_alpha_hosting_readiness.py`: PASS
- `python scripts/validate_public_alpha_launch_candidate.py`: PASS
- `python scripts/public_alpha_smoke.py --json`: PASS
- `python scripts/eureka_public_alpha_ops_posture.py validate --plan .eureka/ops/public-alpha/latest/ops_posture.json --strict`: PASS
- `python scripts/eureka_local_machine_public_exposure.py validate --plan .eureka/public-alpha/exposure/latest/exposure_plan.json --strict`: PASS
- `python scripts/eureka_local_machine_public_exposure.py validate-choice --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json --strict`: PASS
- `python scripts/eureka_search.py "Windows 7 apps" --format json --limit 2`: PASS
- `python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --public-alpha --staging-bundle .eureka/staging/public-alpha --smoke`: PASS
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS

## Public Posture

- Public hosted service launched: false
- Production readiness claimed: false
- Public exposure enabled: false
- Public live source fanout enabled: false
- Public mutation enabled: false
- Public Workbench exposed: false
- Downloads/uploads enabled: false
- Live metadata public mode enabled: false
- Launch approval present: false

## License Posture

```text
LICENSE_UNRESOLVED
```

No license was selected by this task.

## Remaining Blockers

- Provider/public URL decision.
- HTTPS/TLS posture.
- Actual tunnel/proxy rehearsal.
- Full discovery not claimed.
- Release promotion report.
- Manual launch approval.
- Final public launch.
- License selection if the desired public posture is open-source reuse.

## Next Recommended Task

```text
LOCAL-MACHINE-PUBLIC-TUNNEL-PROVIDER-DECISION-00
```
