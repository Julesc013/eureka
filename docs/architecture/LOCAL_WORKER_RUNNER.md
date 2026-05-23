# Local Worker Runner

LOCAL-09 adds the deterministic local worker runner. It is the first execution layer for WorkUnits, but it is deliberately narrow: workers execute queued local records only, through `runtime/local/appliance`, and every run produces an auditable result.

## Role

The runner lives in `runtime/local/worker`. It fetches a WorkUnit from the manifest-backed `workunit_queue`, evaluates the local worker policy, moves the record through queue state transitions, runs an enabled deterministic worker, and records result/audit references in queue metadata.

Enabled worker kinds:

- `noop_worker`
- `review_queue_checker`
- `reviewed_index_rebuild_worker`
- `absence_report_worker`
- `local_status_snapshot_worker`

Blocked worker kinds:

- `source_probe_worker`
- `extraction_worker`
- `agent_research_worker`
- `ai_model_worker`
- `download_worker`
- `install_execute_worker`
- `source_sync_worker`
- `lan_worker`
- `deployment_worker`

## Boundary

Worker runs are not truth acceptance, source approval, evidence acceptance, public launch readiness, or permission to crawl, download, install, execute, call models, expose LAN, or deploy.

LOCAL-09 may mutate only WorkUnit state/history and worker result references. The reviewed-index rebuild worker is the only worker allowed to mutate a product store, and it is operator-token gated with the mutation limited to the local `public_index` store.

## Relationship

LOCAL-09 builds on LOCAL-07 WorkUnits and LOCAL-08 review/rebuild. LOCAL-10 can use this runner for an auto-test and auto-search harness. Future HUNT/F/H workers must add explicit policies before enabling source probes, extraction, model calls, or broader research behavior.

## LOCAL-10 Harness Use

LOCAL-10 does not execute workers from the service. Its harness inspects the
deterministic worker registry and verifies `source_probe_worker`,
`extraction_worker`, and `ai_model_worker` remain blocked. Worker execution
still requires the explicit LOCAL-09 runner command.

## LOCAL-13 Clean-Machine Boundary

LOCAL-13 proves the runner-era Local Appliance can bootstrap and smoke-test
from a clean temp checkout without executing unsafe worker kinds. The
reproducibility proof does not run source probes, extraction, agent research,
model/provider calls, downloads, installation, LAN mutations, or deployment.

## HUNT-07 Background Hunt Use

HUNT-07 uses the LOCAL-09 runner from Search Hunt state. It lists WorkUnits linked through SearchNeeds, chooses only enabled deterministic worker kinds, runs bounded batches, records worker results, and records Search Hunt run history.

Policy-blocked WorkUnits remain blocked. Source probe, extraction, agent research, model/provider, acquisition, source sync, LAN, and deployment workers remain disabled.
