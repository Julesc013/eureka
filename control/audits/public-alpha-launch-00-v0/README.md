# PUBLIC-ALPHA-LAUNCH-00

Status: `WAITING_FOR_MANUAL_LAUNCH_APPROVAL`

The promoted read-only public alpha baseline is ready for an explicit manual
launch task, but no acceptable launch approval record is present.

- current branch: `dev`
- head: `21a64d740d2f79524bd0880121dd65211aec520b`
- origin/main: `21a64d740d2f79524bd0880121dd65211aec520b`
- origin/dev: `21a64d740d2f79524bd0880121dd65211aec520b`
- origin/main...origin/dev: `0 0`
- promotion gate: PASS, 5081 tests
- deployment_performed: false
- public_launch_performed: false
- production_readiness_claimed: false
- public_launch_readiness_claimed: false

Required approval:

- `control/approvals/public-alpha-launch-00-approval.json`
- or `control/inventory/public_alpha_launch_manual_approval.json`

The approval must use the exact phrase `LAUNCH_READ_ONLY_PUBLIC_ALPHA` and must
include target environment, deployment mode, target URL/domain, deployment
command, rollback command, rollback contact, and acknowledged read-only alpha
boundaries.
