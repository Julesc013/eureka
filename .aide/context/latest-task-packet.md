# AIDE Latest Task Packet

## PHASE

HUNT-00 - Search Hunt track planning over Local Appliance

## GOAL

Plan the Search Hunt track over the completed Local Appliance proof surface.

## WHY

LOCAL-14 closed the Local Appliance track with pass_with_warnings. The local
kernel now includes explicit instances, runtime composition, localhost service,
HTML workbench, WorkUnits, review/rebuild, deterministic workers, auto-test and
auto-search, read-only LAN proof, and clean-machine bootstrap proof.

HUNT planning is the preferred next execution spine. SYN planning is an
available alternative. F0 may resume only through the Local Appliance and is not
recommended before the search/eval spine is planned unless the operator chooses
that route explicitly.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `.aide/queue/HUNT-00/task.yaml`
- `control/audits/local-14-local-appliance-closeout-v0/`
- `control/inventory/local_appliance_closeout_result.json`
- `control/inventory/local_appliance_future_track_gate.json`
- `control/inventory/local_appliance_warning_disposition.json`
- `docs/architecture/LOCAL_APPLIANCE_PRODUCT_KERNEL.md`
- `AGENTS.md`

## ALLOWED_PATHS

- HUNT-00 paths must come from a reviewed HUNT-00 task prompt before work starts.
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/HUNT-00/task.yaml`
- HUNT planning docs, validators, inventories, and audit evidence only when explicitly scoped.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- private local files

## IMPLEMENTATION

- Start from `dev` or an explicit HUNT-00 task branch.
- Use the Local Appliance boundaries for all product proof.
- Do not deploy.
- Do not run source probes, crawling, scraping, extraction, or model/provider calls unless a future reviewed prompt explicitly enables them.

## VALIDATION

- `git status --short`
- `git diff --check`
- HUNT-00 focused validator and tests when defined
- Local Appliance closeout references as scoped

## EVIDENCE

- changed files
- validation commands and results
- unresolved risks and deferrals

## NON_GOALS

- No deployment.
- No production readiness claim.
- No public launch readiness claim.
- No unscoped F0 implementation.
- No source probe execution.

## ACCEPTANCE

- HUNT-00 acceptance criteria must come from a future reviewed HUNT-00 prompt.
- Runtime leakage remains a disposed LOCAL warning and blocks automatic main promotion until LOCAL-LEAKAGE-01 or an equivalent review resolves it.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`,
`VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- packet_type: compact_task_packet
- estimated_tokens: 850
- budget_status: PASS
