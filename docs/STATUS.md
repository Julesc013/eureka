# Status

This page carries current-state detail that should not dominate the public
front door. The root [README](../README.md) explains what Eureka is; this page
summarizes what is real now, what is gated, and where to look next.

## Current Maturity

Eureka is a local-first Python reference backend and prototype. It has local
operator workflows, read-only public-alpha route foundations, snapshot/relay
foundations, source-action/source-wave foundations, and governed evals.

Eureka has not been deployed, has not launched publicly, and does not claim
production readiness.

## Branch Posture

| Topic | Current posture |
| --- | --- |
| Normal development branch | `dev` |
| Public front door | `README.md` |
| Volatile development state | this page, bootstrap status, roadmap, runbooks, and audit evidence |
| Queue/operator detail | kept outside the public README unless it changes public posture |
| Product truth | accepted contracts, runtime behavior, reviewed records, and accepted architecture docs |

## Implemented Or Present

| Area | Status |
| --- | --- |
| Python reference backend | Active executable lane |
| Local product loop | Present for local/operator work |
| Workbench/operator loop | Local cockpit foundation present |
| CLI/local web/local HTTP API | Present as local surfaces |
| Public-alpha routes | Read-only foundations present |
| Snapshot/relay | Read-only snapshot-backed foundation present |
| Source Action Kernel | Governed source-action seam present |
| Source Wave | Metadata fixture/mock/governed lanes present |
| Test/eval discipline | Focused lanes plus full-discovery harness/CI posture |
| Rust parity lane | Isolated future/parity lane present |

## Gated, Blocked, Or Deferred

| Area | Current gate |
| --- | --- |
| Public alpha launch | Not launched; requires explicit manual approval and current validation evidence |
| Public deploy dry run | Planned/gated; not a launch claim |
| Public open-internet exposure | Requires hosting, safety, rollback, and operator evidence |
| Live source fanout | Disabled unless future policy/operator approval enables a bounded lane |
| Downloads/uploads/executable actions | Disabled or future-gated |
| Broad extraction | Disabled except safe fixture/member-manifest foundations |
| Model/provider calls | Disabled |
| Native app distribution | Not ready; native work remains a later lane |
| Rust backend replacement | Not ready; Python remains the oracle |

## Current Non-Claims

Eureka does not currently claim:

- deployed public service
- public launch
- production readiness
- full Archive.org search
- full web crawling
- broad corpus coverage
- rights clearance or malware safety
- download, install, execute, upload, app-store, or marketplace behavior
- native client readiness
- live public source fanout
- AI authority or autonomous truth acceptance

## Validation Posture

Use focused lanes during normal development:

```powershell
python scripts/eureka_test_select.py --changed --failed-first --json
python scripts/check_architecture_boundaries.py
```

Use public-alpha checks when touching public-alpha posture:

```powershell
python scripts/validate_public_alpha_readonly.py
python scripts/validate_public_alpha_hosting_readiness.py
python scripts/validate_public_alpha_launch_candidate.py
```

Full unittest discovery is a promotion/nightly/manual lane and should run
through the harness or CI with compact summaries:

```powershell
python scripts/run_full_unittest_discovery.py --out ..\eureka-test-runs\manual_full_discovery
```

## Status Pointers

- [Bootstrap Status](BOOTSTRAP_STATUS.md)
- [Roadmap](ROADMAP.md)
- [Public Alpha Launch Gates](reference/PUBLIC_ALPHA_LAUNCH_GATES.md)
- [Public Alpha Launch Candidate Runbook](operations/PUBLIC_ALPHA_LAUNCH_CANDIDATE_RUNBOOK.md)
- [Public Alpha Deploy Dry-Run Plan](operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md)
- [Test and Eval Lanes](operations/TEST_AND_EVAL_LANES.md)
- [Architecture](ARCHITECTURE.md)
- [Open Questions](OPEN_QUESTIONS.md)
