# Local Instance Readiness Audit

Task: `DEV-TO-MAIN-PROMOTION-READINESS-AND-SYNC-00`

Status: `PASS_WITH_WARNINGS`

## Summary

The current `dev` baseline is usable locally and has read-only public-alpha
foundations. The remaining warnings are launch/posture blockers, not local
execution failures.

## Commands Verified

```powershell
python scripts/eureka_search.py --help
python scripts/eureka_search.py "Windows 7 apps" --format json --limit 2
```

Result: `PASS`

The CLI/local search command exists and returned fixture-backed candidate JSON
without network, mutation, provider calls, live metadata, or public live fanout.

```powershell
python scripts/run_eureka_local.py --help
python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --public-alpha --staging-bundle .eureka/staging/public-alpha --smoke
```

Result: `PASS`

The local public-alpha server wrapper exists. Its `--smoke` path exercised the
staging bundle and exited without leaving a server running. The smoke payload
reported `read_only: true`, `public_mutation_enabled: false`,
`live_metadata_enabled: false`, and `workbench_exposed: false`.

## Validators

- `python scripts/validate_public_alpha_readonly.py`: PASS
- `python scripts/validate_snapshot_relay.py`: PASS
- `python scripts/validate_public_alpha_hosting_readiness.py`: PASS
- `python scripts/validate_public_alpha_launch_candidate.py`: PASS
- `python scripts/public_alpha_smoke.py --json`: PASS, 18 checks
- `python -m unittest tests.docs.test_public_docs -v`: PASS, 4 tests
- `python scripts/check_architecture_boundaries.py`: PASS
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: PASS
- `python scripts/eureka_public_alpha_ops_posture.py validate --plan .eureka/ops/public-alpha/latest/ops_posture.json --strict`: PASS
- `python scripts/eureka_local_machine_public_exposure.py validate --plan .eureka/public-alpha/exposure/latest/exposure_plan.json --strict`: PASS
- `python scripts/eureka_local_machine_public_exposure.py validate-choice --choice .eureka/public-alpha/exposure/operator-choice/latest/operator_choice.json --strict`: PASS
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS

## Known Working Routes Or Commands

- `python scripts/eureka_search.py "Windows 7 apps" --format json --limit 2`
- `python scripts/run_eureka_local.py --host 127.0.0.1 --port 8765 --public-alpha --staging-bundle .eureka/staging/public-alpha --smoke`
- `/api/status`
- `/api/search?q=synthetic`
- `/api/v1/status`
- `/api/v1/search?q=windows+7+apps`
- `/record/{id}`

## Remaining Gaps

- Provider/public URL decision is missing.
- Provider HTTPS/TLS posture is unvalidated.
- Actual tunnel/proxy rehearsal has not run.
- Full discovery is not claimed in this task.
- License remains unresolved for open-source reuse posture.
