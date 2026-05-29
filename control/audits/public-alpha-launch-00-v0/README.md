# PUBLIC-ALPHA-LAUNCH-00

Status: `WAITING_FOR_MANUAL_LAUNCH_APPROVAL`

The promoted read-only public alpha baseline is ready for an explicit manual
launch task, but no acceptable launch approval record is present.

- current branch: `dev`
- launch baseline head: `21a64d740d2f79524bd0880121dd65211aec520b`
- current dev head after waiting evidence: `37648cd4c58308dc884df8c1e9a8b39acdce2de2`
- origin/main: `21a64d740d2f79524bd0880121dd65211aec520b`
- origin/dev: `37648cd4c58308dc884df8c1e9a8b39acdce2de2`
- origin/main...origin/dev: `0 1`
- dev ahead of main only by waiting approval evidence: true
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
