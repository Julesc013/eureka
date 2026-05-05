# Public Search Runtime Integration Audit

P100 is an audit-only checkpoint for public search runtime wiring. It changes no
routes, responses, ordering, hosted behavior, telemetry, source access, dry-run
runtime integration, or mutation boundary.

## Classification Values

Use only:

- `implemented_public_runtime`
- `implemented_local_runtime`
- `implemented_local_dry_run`
- `implemented_static_artifact`
- `contract_only`
- `planning_only`
- `approval_gated`
- `operator_gated`
- `disabled`
- `absent`
- `blocked`
- `unexpected_integration`

## Current Runtime Boundary

Public search is a local/prototype `local_index_only` runtime. It reads controlled
public/local index records and governed source registry summaries. It exposes
`/search`, `/api/v1/search`, `/api/v1/query-plan`, `/api/v1/status`,
`/api/v1/sources`, and `/api/v1/source/{source_id}` locally.

Hosted public search is not verified. Static search handoff is present, but the
hosted backend URL is unconfigured.

## Integrated Now

- Local public search runtime.
- Public result-card projection.
- Deterministic query-plan projection.
- Generated public index/static summary artifacts.
- Static search handoff with backend-unconfigured posture.

## Not Integrated Now

- Source-cache dry-run runtime.
- Evidence-ledger dry-run runtime.
- Query observation runtime.
- Object/source/comparison page runtime.
- Connector runtimes and live source fanout.
- Pack import runtime.
- Deep extraction runtime.
- Search-result explanation runtime.
- Public search ranking runtime.

## Dry-Run Boundary

P98 source-cache and P99 evidence-ledger runtimes are local dry-runs over approved
repo examples. They are not authoritative stores and public search must not read
them as source truth or evidence truth.

## Mutation And Safety Boundaries

Public search must not mutate source cache, evidence ledger, result cache, miss
ledger, search need records, probe queue, candidate index, public index, local
index, runtime index, or master index. It must not perform live external fanout,
arbitrary URL fetching, uploads, downloads, installs, execution, package-manager
invocation, emulator/VM launch, telemetry, accounts, or hidden ranking.

## Validator

Run:

```bash
python scripts/validate_public_search_runtime_integration_audit.py
python scripts/validate_public_search_runtime_integration_audit.py --json
python scripts/report_public_search_runtime_integration_status.py --json
```

The validator checks the audit pack, inventory, report JSON, classifications,
hard booleans, status files, mutation boundary, and no-integration claims.

## Interpreting Blockers

`operator_gated` means a human/operator deployment or policy gate is still
required. `approval_gated` means governed approval packs or review decisions are
not enough to create runtime behavior. `unexpected_integration` means public
search is wired to something that should remain dry-run, planning-only,
contract-only, disabled, or absent, and must be treated as a blocker.

## Next Steps

Next recommended branch: `P101 Connector Approval and Runtime Planning Audit v0`.

Human/operator parallel work remains hosted wrapper deployment, backend URL
configuration, edge/rate-limit configuration, static-site verification, Manual
Observation Batch 0 execution, and review of authoritative source-cache and
evidence-ledger storage policies.

