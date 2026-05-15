# Search Hunt Workflow Smoke

`scripts/eureka_hunt_workflow_smoke.py` runs the full local deterministic workflow for `sampleproject` and a missing-query hunt.

It requires:

- `--instance <path>`
- `--operator-token <token>`

It emits JSON fields for each stage and explicit false boundary flags for source probes, extraction, external network, model providers, download/install/execute, site/dist mutation, master-index mutation, deployment, and public/production readiness claims.
