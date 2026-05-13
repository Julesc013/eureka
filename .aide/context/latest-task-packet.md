# AIDE Latest Task Packet

## PHASE

LOCAL-04 - Read-only localhost HTTP service over reviewed index

## GOAL

Add a read-only localhost HTTP service over the reviewed public index through
the LOCAL-03 `runtime/local_appliance` composition boundary.

## WHY

LOCAL-03 completed the local appliance runtime composition boundary. The next
local appliance step is a localhost-only read surface that uses
`open_local_appliance(instance_path, read_only=True)` rather than opening store
paths directly. This packet keeps the implementation bounded and preserves the
LOCAL track gates: no HTML workbench, no LAN exposure, no deployment, no source
probes, no write routes, and no production/public launch claim.

## CONTEXT_REFS

- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-03/task.yaml`
- `.aide/queue/LOCAL-04/task.yaml`
- `.aide/context/repo-snapshot.json` (present)
- `.aide/context/repo-map.json` (present)
- `.aide/context/repo-map.md` (present)
- `.aide/context/test-map.json` (present)
- `.aide/context/context-index.json` (present)
- `.aide/context/latest-context-packet.md` (present)
- `.aide/routing/latest-route-decision.json` (present)
- `.aide/routing/latest-route-decision.md` (present)
- `.aide/cache/latest-cache-keys.json` (present)
- `.aide/cache/latest-cache-keys.md` (present)
- `runtime/local_appliance/`
- `docs/architecture/LOCAL_RUNTIME_COMPOSITION_BOUNDARY.md`
- `docs/reference/LOCAL_APPLIANCE_RUNTIME_API.md`
- `docs/operations/LOCAL_RUNTIME_COMPOSITION.md`
- `control/inventory/local_03_next_task_decision.json`
- `AGENTS.md`
- `.aide/prompts/compact-task.md`
- `.aide/policies/token-budget.yaml`
- `.aide/policies/cache.yaml`
- `.aide/policies/local-state.yaml`

## ALLOWED_PATHS

- `.aide/queue/LOCAL-04/**`
- `.aide/context/**`
- `runtime/local_appliance/**`
- localhost-only service module paths explicitly introduced for LOCAL-04
- focused LOCAL-04 validators and tests under `scripts/**` and `tests/**`
- `docs/architecture/**`, `docs/reference/**`, and `docs/operations/**` only
  when documenting the LOCAL-04 service boundary
- `control/inventory/**` and `control/audits/local-04-*/**` for LOCAL-04
  policy, inventory, and evidence artifacts

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `contracts/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- raw provider credentials, API keys, local caches, raw prompt logs
- broad `runtime/**` changes outside `runtime/local_appliance/**` and the
  LOCAL-04 localhost service boundary
- write routes, source probes, index rebuilds, WorkUnit runtime, HTML workbench,
  LAN binding, deployment, provider/model calls, production readiness claims,
  public launch claims, and app-surface work outside the LOCAL-04 localhost
  service boundary

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-04 task branch from `dev`.
- Read `.aide/queue/LOCAL-04/task.yaml` and the LOCAL-03 runtime composition
  docs before editing.
- Preflight blocker: `py -3 scripts/validate_local_runtime_composition.py`
  currently fails because the runtime leakage scan exceeds the older LOCAL-03
  baseline. Reconcile that validation drift before accepting LOCAL-04.
- Route all local instance/store access through `runtime/local_appliance` and
  `open_local_appliance(instance_path, read_only=True)`.
- Keep the HTTP surface localhost-only and read-only.
- Add focused validators, tests, docs, and audit evidence for the service
  boundary.
- Preserve generated/manual boundaries and avoid broad product refactors.
- Make no Eureka product behavior change outside the LOCAL-04 localhost
  read-only service boundary.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py index`
- `py -3 .aide/scripts/aide_lite.py context`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py route explain`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 scripts/check_architecture_boundaries.py`
- `py -3 scripts/validate_local_runtime_composition.py`
- LOCAL-04 focused validator and tests when defined
- `git diff --check`

## COMMITS

- Commit coherent subdeliverables with verbose bodies.
- Stop at review gates.

## EVIDENCE

- changed files grouped by purpose
- LOCAL-04 audit/evidence packet
- validation commands and results
- localhost-only/read-only proof
- runtime composition boundary proof
- verifier/review packet result when available
- compact packet size and budget status
- unresolved risks and deferrals

## NON_GOALS

- No HTML workbench implementation.
- No WorkUnit runtime implementation.
- No LAN binding.
- No deployment.
- No source probe execution.
- No index rebuild behavior.
- No provider/model calls.
- No production readiness claim.
- No public launch readiness claim.

## ACCEPTANCE

- LOCAL-04 acceptance criteria are met.
- LOCAL-03 runtime composition validation is passing again, or any remaining
  leakage drift is separately reviewed and explicitly accepted.
- Service code uses the LOCAL-03 runtime composition boundary.
- HTTP service is localhost-only and read-only.
- No write routes, source probes, index rebuilds, HTML workbench, LAN,
  deployment, production readiness claim, or public launch claim are added.
- Validation is run and recorded.
- Evidence is written.
- F0 remains deferred until LOCAL-14.
- No secrets, raw prompt logs, local caches, or `.aide.local` contents are
  committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, route/verifier/token results, `RISKS`, and `NEXT`.
Include the verifier result when Q12 verifier behavior is available.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 6157
- approx_tokens: 1540
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`
