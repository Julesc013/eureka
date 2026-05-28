# Operations Docs

This directory contains runbooks, safety policies, review gates, and validation
procedures. Operational docs should be treated as instructions and evidence
records, not as proof that a capability has launched.

## Start Here

- [Test and Eval Lanes](TEST_AND_EVAL_LANES.md)
- [Public Alpha Launch Candidate Runbook](PUBLIC_ALPHA_LAUNCH_CANDIDATE_RUNBOOK.md)
- [Public Alpha Deploy Dry-Run Plan](PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md)
- [Public Alpha Manual Approval Gate](PUBLIC_ALPHA_MANUAL_APPROVAL_GATE.md)
- [Local HTML Workbench Runbook](LOCAL_HTML_WORKBENCH_RUNBOOK.md)
- [Local Apply Gate Runbook](LOCAL_APPLY_GATE_RUNBOOK.md)
- [Source Action Kernel Runbook](SOURCE_ACTION_KERNEL_RUNBOOK.md)
- [Snapshot Relay Runbook](SNAPSHOT_RELAY_RUNBOOK.md)

## Current Operating Posture

Eureka has local/operator and read-only public-alpha foundations. Deployment,
public launch, production readiness, public mutation, public live source fanout,
downloads, uploads, broad extraction, and model/provider calls remain unclaimed
or disabled.

Full unittest discovery is not a normal in-chat AI validation step. Use the
harness or CI and preserve compact summaries:

```powershell
python scripts/run_full_unittest_discovery.py --out ..\eureka-test-runs\manual_full_discovery
```
