# Integration Status Matrix

Valid classifications:

`implemented_public_runtime`, `implemented_local_runtime`,
`implemented_local_dry_run`, `implemented_static_artifact`, `contract_only`,
`planning_only`, `approval_gated`, `operator_gated`, `disabled`, `absent`,
`blocked`, `unexpected_integration`.

| Area | Classification | Public search integrated now? | Notes |
| --- | --- | --- | --- |
| Public search API | `implemented_local_runtime` | yes, local only | `/search` and `/api/v1/*` local prototype routes exist in `local_index_only` mode. |
| Local public search runtime | `implemented_local_runtime` | yes, local only | Uses controlled local/public index records and deterministic planner projection. |
| Hosted public search runtime | `operator_gated` | no | P77 evidence keeps hosted backend unconfigured and static URL verification failed. |
| Public index | `implemented_static_artifact` | yes | Generated public-safe local-index artifact with 584 documents. |
| Static search handoff | `implemented_static_artifact` | yes, static only | Search page and JSON config exist; backend URL is not configured. |
| Source cache dry-run | `implemented_local_dry_run` | no | P98 CLI/report only; no authoritative store. |
| Evidence ledger dry-run | `implemented_local_dry_run` | no | P99 CLI/report only; no authoritative ledger. |
| Query observation | `planning_only` | no | No runtime observation store, telemetry, or raw query retention. |
| Object/source/comparison pages | `planning_only` | no | Contracts and planning exist; no runtime routes. |
| Connector runtimes | `approval_gated` | no | Approval/planning packs exist; live calls disabled. |
| Pack import | `planning_only` | no | Validate/planning/quarantine contracts exist; runtime import absent. |
| Deep extraction | `contract_only` | no | Schemas/examples only; no extraction runtime. |
| Search result explanation | `contract_only` | no | Contract exists; public response unchanged by explanation runtime. |
| Ranking runtime | `planning_only` | no | P97 planning only; public order unchanged. |
| Telemetry/accounts/uploads/downloads | `disabled` | no | Safety guard blocks or omits these capabilities. |

