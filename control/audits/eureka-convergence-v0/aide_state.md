# AIDE State

## Current Artifacts

- Latest task packet: `.aide/context/latest-task-packet.md`.
- Latest review packet: `.aide/context/latest-review-packet.md`.
- AIDE operating handoff: `.aide/reports/eureka-aide-lite-operating-handoff.md`.
- Repo-health report: `.aide/reports/eureka-repo-health.md`.
- Repo-health JSON: `.aide/reports/eureka-repo-health.json`.
- Queue index: `.aide/queue/index.yaml`.
- Current queue item before this audit: `EUREKA-CONVERGE-01`.

## Validation Summary

- `doctor`: PASS.
- `validate`: PASS, with review-packet optional-reference warnings.
- `test`: PASS.
- `selftest`: PASS.
- `verify`: WARN-only, 0 errors.
- `eval list`: PASS, 12 active golden tasks.
- `eval run`: PASS, 12/12.
- `adapter validate`: PASS.
- `scripts/check_architecture_boundaries.py`: PASS.

## Known WARN-only Conditions

- Optional AIDE controller recommendations report may be absent.
- Optional AIDE gateway status report may be absent.
- Optional AIDE provider status report may be absent.
- Future queue evidence references may warn until the future task has executed.
- Pre-commit diff-scope warnings may appear while the current evidence is
  uncommitted and the active queue points to the next task.

## Future-Agent Read Order

1. `.aide/context/latest-task-packet.md`
2. `.aide/reports/eureka-aide-lite-operating-handoff.md`
3. `.aide/reports/eureka-repo-health.md`
4. `control/audits/eureka-convergence-v0/README.md`
5. `AGENTS.md`

## Boundary

AIDE Lite is repo-operating metadata and validation support. It may help create
compact packets, evidence, queue plans, and deterministic audits. It must not
define archive truth, runtime behavior, hosted deployment claims, connector
approval, public data truth, native behavior, or AI truth.
