# Connector Approval Runtime Planning Audit

P101 records the factual approval and runtime-planning status for the first-wave
connectors:

- `internet_archive_metadata`
- `wayback_cdx_memento`
- `github_releases`
- `pypi_metadata`
- `npm_metadata`
- `software_heritage`

This is the connector set for the P101 audit.

Classification values are:

`approval_pack_missing`, `approval_pack_present`, `approval_pending`,
`approval_complete_future`, `contract_only`, `planning_only`,
`runtime_plan_missing`, `runtime_plan_present`,
`local_dry_run_ready_after_operator_approval`,
`source_sync_worker_ready_after_operator_approval`, `operator_gated`,
`approval_gated`, `policy_gated`, `dependency_gated`, `blocked`, `disabled`,
`implemented_local_dry_run`, `implemented_runtime`, and
`unexpected_runtime_or_live_integration`.

Approval packs are not runtime. Runtime plans are not runtime implementation.
The current aggregate status is approval-gated.

Required gates before implementation include source/API policy review,
User-Agent/contact policy, rate limits, timeouts, retry/backoff, circuit
breakers, token/auth policy, identity/privacy policy, and approved
source-cache/evidence-ledger destinations.

Public search must not call connectors live, accept connector/live/source URL
parameters, or expose public-query fanout. Connector outputs, if approved later,
must flow through source cache and evidence ledger boundaries before any reviewed
public index projection.

Mutation remains disabled for source cache, evidence ledger, candidate index,
public index, local index, runtime index, and master index.

Run:

- `python scripts/validate_connector_approval_runtime_planning_audit.py`
- `python scripts/validate_connector_approval_runtime_planning_audit.py --json`
- `python scripts/report_connector_approval_runtime_status.py --json`

Next step: P102 Manual Observation Batch 0 Follow-up Plan v0 if manual
observations remain pending.
