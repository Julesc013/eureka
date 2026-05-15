# Background Hunt Runner

HUNT-07 adds a background runner for Search Hunts that already have linked SearchNeeds and WorkUnits.

The runner is intentionally narrow. It plans and runs only deterministic local worker kinds that LOCAL-09 already allows:

- `noop_worker`
- `review_queue_checker`
- `absence_report_worker`
- `local_status_snapshot_worker`
- `reviewed_index_rebuild_worker`, with its existing operator-token gate

Blocked worker kinds stay blocked:

- `source_probe_worker`
- `extraction_worker`
- `agent_research_worker`
- `ai_model_worker`
- `download_worker`
- `install_execute_worker`
- `source_sync_worker`
- `lan_worker`
- `deployment_worker`

## Modes

- `plan_only` classifies linked WorkUnits and records no worker result.
- `run_next` runs one safe queued WorkUnit.
- `run_batch` runs a bounded set of safe queued WorkUnits, with a maximum of ten.
- `summarize` reports plan, latest run, run history, runnable counts, and blocked counts.

## Non-Claims

A run result is not truth. A completed WorkUnit is not evidence acceptance. Policy-blocked WorkUnits are not failures; they are local signals that future gates remain closed.

Source probes, extraction, model/provider calls, acquisition actions, source sync, LAN worker mutation, deployment, and master index mutation remain disabled.

## Relationship

HUNT-07 proves the hunt loop can make safe local progress before HUNT-08 workbench smoke integration and before any future source, extraction, AI, SYN, or F0 gates.
## HUNT-08 Integration

The background hunt runner is exercised by the workbench integration smoke as one safe deterministic worker execution. Policy-blocked source-probe, extraction, and AI/model worker records remain blocked and visible.
## Agent Research Boundary

Background hunt runner work remains deterministic and local. HUNT-09 agent research task drafts are visible beside Hunt and SearchNeed state, but they are not runnable WorkUnits and do not enable model providers, browsers, source probes, or extraction.

