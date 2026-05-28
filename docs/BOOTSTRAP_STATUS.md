# Bootstrap Status

Eureka is beyond empty bootstrap, but still pre-product. The current baseline is
a local-first Python reference backend with a promoted local product loop,
read-only public-alpha route foundations, snapshot/relay foundations, source
action/source wave foundations, and a passed public-alpha launch-candidate gate.

This document is a status summary, not a production or launch claim.

## Current Baseline

| Area | Status |
| --- | --- |
| Python reference backend | Active executable lane |
| Local product loop | Promoted |
| Workbench/operator loop | Local cockpit foundation present |
| Public-alpha routes | Read-only foundations present |
| Snapshot/relay | Read-only snapshot-backed foundation present |
| Source Action Kernel | Governed source-action seam present |
| Source Wave | Metadata fixture/mock/governed lanes present |
| Launch candidate gate | Passed; recommends deploy dry run |
| Deployment | Not performed |
| Public launch | Not performed |
| Production readiness | Not claimed |

The promoted public-alpha read-only baseline was recorded at
`ba70874c2bd0fdf7c2a3e32577d24dc7ee909dc8`. The later
`PUBLIC-ALPHA-LAUNCH-CANDIDATE-00` evidence records a pass and recommends
`PUBLIC-ALPHA-DEPLOY-DRY-RUN-00`. That recommendation is not deployment and not
public launch approval.

## What Works Locally

- Instance validation through `scripts/eureka_validate_instance.py`.
- Local stdlib server through `scripts/eureka_local_server.py`.
- Local Workbench/operator loop for query, resolution run, lanes, candidates,
  review, promotion preview, local apply, reviewed result, and rollback.
- Read-only public-alpha pages and `/api/v1/alpha/*` endpoints.
- Focused validators for public alpha, hosting readiness, snapshot relay,
  source wave, source action kernel, and architecture boundaries.
- Full unittest discovery harness that writes compact summaries outside the
  repository.

## Read-Only Public Alpha Posture

Public alpha is snapshot-backed and read-only:

- public live source fanout: disabled
- public mutation: disabled
- downloads/uploads: disabled
- extraction: disabled except safe fixture/member-manifest foundations
- model/provider calls: disabled
- local/master/public index mutation: review/promotion-gated, not automatic

## Testing Posture

Use focused lanes during normal development:

```powershell
python scripts/eureka_test_select.py --changed --failed-first --json
```

Use the gate wrapper for public-alpha closeout style checks:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --watch --clean
```

Run full unittest discovery outside AI chat/model sessions:

```powershell
python scripts/run_full_unittest_discovery.py --out ..\eureka-test-runs\manual_full_discovery
```

AI agents should read compact summaries and handoffs, not raw full-discovery
logs.

## Current Non-Claims

Eureka does not currently claim:

- deployed public service
- public launch readiness
- production readiness
- full Archive.org search
- full web crawler behavior
- broad corpus coverage
- download, install, execute, upload, or app-store behavior
- native client readiness
- marketplace/action-layer readiness
- live public source fanout
- AI authority or autonomous truth acceptance

## Pointers

- Root overview: [../README.md](../README.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Roadmap: [ROADMAP.md](ROADMAP.md)
- Test and eval lanes: [operations/TEST_AND_EVAL_LANES.md](operations/TEST_AND_EVAL_LANES.md)
- Public alpha launch gates: [reference/PUBLIC_ALPHA_LAUNCH_GATES.md](reference/PUBLIC_ALPHA_LAUNCH_GATES.md)
