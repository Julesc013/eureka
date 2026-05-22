# AIDE Release Notes Preview

This is a deterministic preview only. It does not publish a release.

source_range: HEAD latest 50 commits
source_head: df6a6967afdb510de46651f70e21541f20b6741b
preview_only: true

## Highlights

- Added: compatibility handling for historical candidate/probe/OBS references after schema moves. (5f5e5bcb22d2)
- Added: source observation seam behavior and audit evidence for R0-04. (8bb9e4cd0bf5)
- Added: durable source cache SQLite persistence seam for R0-05. (1a48f6f3fb76)
- Added: source cache store contracts, docs, tests, validator, and audit pack. (1a48f6f3fb76)
- Added: durable evidence ledger SQLite persistence seam for R0-06. (a9c536dfe1f9)
- Added: evidence ledger contracts, docs, tests, validator, and audit pack. (a9c536dfe1f9)
- Added: durable review queue store package and governed store contracts. (0eea9c54c65a)
- Added: init, demo, validator, docs, inventory, and audit pack for R0-07. (0eea9c54c65a)
- Added: reviewed public index store and rebuild pipeline. (f9d7fc25f9fd)
- Added: public index store schemas. (f9d7fc25f9fd)
- Added: store, rebuild, search, absence, and integration tests. (f9d7fc25f9fd)
- Added: reviewed public index architecture, reference, and operations docs. (f9d7fc25f9fd)
- Added: one-source PyPI live metadata pipeline and audit evidence. (90695310dc30)
- Added: R0-10 production recovery review evidence and scripts. (6eeae5b324a5)
- Added: R0 final closeout evidence and scripts. (0da3111215d2)
- Added: R0 contract taxonomy remediation scripts, tests, inventories, docs, and audit pack (ede77d3cb101)
- Added: generated artifact drift policy and validation tooling. (dbc4e72ccf63)
- Added: legacy leakage remediation scripts, tests, inventories, docs, and audit pack. (be01503a76b0)
- Added: final R0 promotion review inventories, audit pack, docs, and merge plan. (4cde57bd1004)
- Added: dev-to-main R0 promotion evidence and F0 start decision. (387a307d0397)
- Added: Local Appliance track policies, inventories, docs, audit pack, validator, and tests. (a140304235d7)
- Added: LOCAL-01 local instance bootstrap controls and commands. (7f373983b227)
- Added: local instance schema and migration policies. (9bdad0968762)
- Added: store manifest, migration state, schema-version inventories, audit pack, validator, migration status command, and focused tests. (9bdad0968762)
- Added: runtime status, composition demo, and LOCAL-03 validator scripts. (ac9f5b8de4f6)
- Added: LOCAL-03 policies, inventories, tests, docs, queue handoff, and audit evidence. (ac9f5b8de4f6)
- Added: runtime/local_appliance runtime composition API. (5f9ac9870626)
- Added: runtime status, composition demo, and LOCAL-03 validator scripts. (5f9ac9870626)
- Added: LOCAL-03 policies, inventories, tests, docs, queue handoff, and audit evidence. (5f9ac9870626)
- Added: runtime/local_service read-only localhost service API. (15a46c118f90)
- Added: local server, smoke, and LOCAL-04 validator scripts. (15a46c118f90)
- Added: LOCAL-04 policies, inventories, docs, queue handoff, tests, and audit evidence. (15a46c118f90)
- Added: server-rendered local workbench runtime, smoke script, validator, policies, inventories, docs, tests, and audit pack. (e0af786e11e0)
- Added: LOCAL-06 page hardening policies, inventories, validator, tests, docs, and audit pack. (fb230b12543f)
- Added: durable local WorkUnit queue store, state machine, records, queries, and validation. (10b8beb7364a)
- Added: WorkUnit queue CLI, demo, and validator. (10b8beb7364a)
- Added: local operator auth, local review service, review/rebuild routes, scripts, tests, policies, inventories, docs, and audit pack. (ff941a760345)
- Added: runtime/local_worker, worker runner scripts, LOCAL-09 policies, inventories, docs, tests, validator, queue handoff, and audit pack. (5488d5b29987)
- Added: target-local Git workflow detection and helper planning reports. (3e5302ea9a36)
- Added: Q32 final evidence and review-gate status. (1e67573e29a1)
- Added: deterministic local auto-test and auto-search harness commands. (db42e120c3f5)
- Added: machine-readable and Markdown eval reports with latency and safety posture. (db42e120c3f5)
- Added: read-only LAN safety policy package, LAN route/mutation matrices, policy check script, validator, docs, and audit pack. (285d0c4dcd4b)
- Added: LOCAL-12 LAN smoke/probe/shutdown scripts, validator, policies, inventories, tests, docs, and audit pack. (9bddfc02d506)
- Added: LOCAL-13 clean-machine scripts, validator, policies, inventories, tests, docs, and audit pack. (d3cf4ea25532)
- Added: LOCAL-14 closeout scripts, inventories, docs, tests, audit pack, and task stubs. (e39101948499)
- Added: final green inventories and audit evidence. (736a43a5a9c5)
- Added: LOCAL total remediation inventories, audit evidence, and promotion gate tests. (4e9ebd7478ae)
- Added: final state inventories, audit pack, future execution plan, and chat alignment packet. (7de5c8b708c2)
- Changed: active validators and tests now follow the R0 contract taxonomy for moved control schemas. (5f5e5bcb22d2)
- Changed: R0-03B-2 validation evidence now records the final full-suite pass. (5f5e5bcb22d2)
- Changed: contract taxonomy scanner recognizes the required evidence_candidate runtime contract as product runtime. (8bb9e4cd0bf5)
- Changed: contract taxonomy inventory includes the new store contracts. (1a48f6f3fb76)
- Changed: contract taxonomy durable-store classification handles store contracts before preview naming signals. (a9c536dfe1f9)
- Changed: contract taxonomy classification now treats contracts/stores as durable store contracts before task-queue filename heuristics. (0eea9c54c65a)
- Changed: integrate remote dev cleanup commit into local dev history. (ce1ab9685222)
- Changed: merge R0 recovery branch into dev. (9cda6e786c25)
- Changed: refreshed exact runtime leakage allowlist hashes after reference-only path updates. (d15eb701b478)
- Changed: refreshed governed generated artifacts and R0 closeout decision evidence. (dbc4e72ccf63)
- Changed: quarantine legacy H-series connector prototype runtime and update references. (be01503a76b0)
- Changed: AIDE queue, task packet, review packet, and repo health now route to LOCAL-01 before F0. (a140304235d7)
- Changed: queue state advances to LOCAL-02 while F0 remains deferred. (7f373983b227)
- Changed: init, validate, and status scripts now understand versioned instance metadata. (9bdad0968762)
- Changed: refreshed AIDE handover evidence and compact task/review artifacts. (cf0c53a41d93)
- Changed: local service now serves read-only HTML routes while keeping JSON API routes under /api/v1. (e0af786e11e0)
- Changed: local workbench view models and pages now expose operational status, provenance, absence layers, non-claims, and unavailable capabilities. (fb230b12543f)
- Changed: local service search JSON now preserves existing result fields while adding full reviewed record fields when available. (fb230b12543f)
- Changed: local instance manifest, runtime composition, and status now include the WorkUnit queue store. (10b8beb7364a)
- Changed: LOCAL-07 policies, inventories, audit pack, leakage baseline, and queue handoff. (10b8beb7364a)
- Changed: local service and workbench routes now expose operator-gated review/rebuild pages and APIs. (ff941a760345)
- Changed: WorkUnit queue now records worker result and audit payload references. (5488d5b29987)
- Changed: imported canonical AIDE governance and validation tooling into Eureka. (21e4f766300d)
- Changed: regenerated Eureka-local AIDE packets and governance reports. (5d955486e323)
- Changed: refreshed agent guidance for structured commits, task recovery, and Git plan usage. (4c954e516a20)
- Changed: refreshed final Q32 reports and token metadata. (1e67573e29a1)
- Changed: local server now requires explicit --bind-lan for all-interface bind hosts and blocks LAN unsafe routes. (285d0c4dcd4b)
- Changed: AIDE queue/context/repo-health to hand off to LOCAL-13. (9bddfc02d506)
- Changed: AIDE queue/context/repo-health to hand off to LOCAL-14. (d3cf4ea25532)
- Changed: AIDE queue/context/repo-health to hand off from LOCAL-14 to HUNT-00. (e39101948499)
- Changed: completed LOCAL validators accept advanced queue state. (736a43a5a9c5)
- Changed: final green evidence records one additional safe repair. (698e30097344)
- Changed: LOCAL closeout warning and promotion evidence now reflect zero new unallowlisted leakage findings. (4e9ebd7478ae)
- Changed: promotion evidence now records the completed fast-forward promotion. (52a73c641d2c)
- Changed: LOCAL-14 promotion review evidence restored to plan-only semantics. (7de5c8b708c2)
- Changed: local AIDE control plane upgraded and Q56 Existing Tool Absorption packet generated. (df6a6967afdb)
- Fixed: preserve candidate-index historical contract path compatibility during merge. (ce1ab9685222)
- Fixed: moved unresolved contract taxonomy artifacts to contracts/control_schemas (ede77d3cb101)
- Fixed: updated active schema references and audit evidence needed by validators (ede77d3cb101)
- Fixed: retired remaining contract taxonomy blockers and shims. (d15eb701b478)
- Fixed: isolated static site JSON build test from site/dist. (dbc4e72ccf63)
- Fixed: classified HTML heading tags and local-bundle fixture wording as leakage false positives. (dbc4e72ccf63)
- Fixed: LAN client host handling is separated from service bind-host validation. (285d0c4dcd4b)
- Fixed: stale IA readiness and local workbench test expectations. (736a43a5a9c5)
- Fixed: refreshed stale public search generated artifacts. (698e30097344)
- Fixed: runtime leakage path classification now treats nested product tests as test fixtures before production paths. (4e9ebd7478ae)
- Fixed: runtime leakage term matching keeps uppercase governance tokens case-sensitive. (4e9ebd7478ae)
- Fixed: runtime leakage glob matching handles mid-pattern ** fixture paths. (4e9ebd7478ae)
- Docs: added R0 production review, dev-to-main promotion review, and F0 resumption gate notes. (6eeae5b324a5)
- Docs: added final closeout, limitations, F0 handoff, branch/queue, future completion, and recovered seam docs. (0da3111215d2)
- Docs: recorded generated artifact drift as a child remediation blocker. (d15eb701b478)
- Docs: branch state, rollback, and non-claim evidence. (387a307d0397)
- Docs: WorkUnit queue boundary, API, state machine, and runbook. (10b8beb7364a)
- Docs: recorded source-pack and baseline validation evidence. (5d31441b87f5)
- Docs: documented canonical AIDE governance sync for Eureka. (4c954e516a20)
- Docs: LOCAL auto-test harness, auto-search suites, report format, and runbook. (db42e120c3f5)
- Docs: added LAN mode, route matrix, safety gate, operator boundary, and smoke prereq docs. (285d0c4dcd4b)
- Docs: LAN smoke test, external-client checklist, shutdown cleanup, limitations, route matrix, and service runbook updates. (9bddfc02d506)
- Docs: clean-machine bootstrap, smoke, external proof, reproducibility, and clean-state runbooks. (d3cf4ea25532)
- Docs: product kernel, capability map, closeout, future task gate, remaining warnings, HUNT/SYN/F0 handoff, promotion review, and post-LOCAL execution spine. (e39101948499)
- Tests: full unittest discovery passes on the final R0-03B-2 tree. (5f5e5bcb22d2)
- Tests: review queue behavior, migration, and integration coverage. (0eea9c54c65a)
- Tests: added offline and mocked-live coverage for the one-source gate. (90695310dc30)
- Tests: added production review and promotion-plan operation tests. (6eeae5b324a5)
- Tests: added final closeout, safe repair, and future task gate tests. (0da3111215d2)
- Tests: added focused generated-artifact drift and isolation tests. (dbc4e72ccf63)
- Tests: promotion audit and dev-to-main merge plan operation coverage. (4cde57bd1004)
- Tests: merge evidence validator coverage. (387a307d0397)
- Tests: focused local instance bootstrap and policy tests. (7f373983b227)
- Tests: added LOCAL-02 migration guard and schema-version operation tests. (9bdad0968762)
- Tests: focused runtime and operations coverage for composition, status, read-only mode, close idempotency, forbidden roots, unsupported schema fail-closed, and scripts. (ac9f5b8de4f6)
- Tests: focused runtime and operations coverage for composition, status, read-only mode, close idempotency, forbidden roots, unsupported schema fail-closed, and scripts. (5f9ac9870626)
- Tests: focused runtime and operations coverage for routes, read-only enforcement, host rejection, smoke, validator, and import hygiene. (15a46c118f90)
- Tests: page hardening focused tests and smoke assertions cover the new markers. (fb230b12543f)
- Tests: focused runtime and operations tests for queue behavior and scripts. (10b8beb7364a)
- Tests: added portable governance tests and golden tasks. (21e4f766300d)
- Tests: focused local eval runtime and operation script coverage. (db42e120c3f5)
- Tests: added focused runtime and operations tests for LAN hosts, policy, service gate, and scripts. (285d0c4dcd4b)
- Tests: focused LAN smoke policy, read-only route, mutation blocking, client scope, and script tests. (9bddfc02d506)
- Tests: clean-machine bootstrap, smoke, and report operation tests. (d3cf4ea25532)
- Tests: LOCAL closeout, future gate, handoff, and promotion review operation tests. (e39101948499)
- Tests: final-state, final-future-plan, and final-chat-alignment guard tests added. (7de5c8b708c2)

## Validation Summary

- 5f5e5bcb22d2: `git diff --check`: PASS.
- 5f5e5bcb22d2: `git diff --check`: PASS.
- 5f5e5bcb22d2: `git diff --check`: PASS.
- 5f5e5bcb22d2: `git diff --check`: PASS.
- 8bb9e4cd0bf5: PASS: git status --short
- 8bb9e4cd0bf5: PASS: git status --short
- 1a48f6f3fb76: PASS: git diff --check
- 1a48f6f3fb76: PASS: git diff --check
- 1a48f6f3fb76: PASS: git diff --check
- a9c536dfe1f9: PASS: git diff --check

## Known Risks

- 5f5e5bcb22d2: Remaining unresolved contracts block R0-04 until R0-03C or an allowed cleanup handles active consumers.
- 5f5e5bcb22d2: Remaining unresolved contracts block R0-04 until R0-03C or an allowed cleanup handles active consumers.
- 5f5e5bcb22d2: Remaining unresolved contracts block R0-04 until R0-03C or an allowed cleanup handles active consumers.
- 5f5e5bcb22d2: Remaining unresolved contracts block R0-04 until R0-03C or an allowed cleanup handles active consumers.
- 8bb9e4cd0bf5: R0-03B-2 still records unresolved legacy contract taxonomy debt, so this closes as PASS_WITH_WARNINGS.
- 8bb9e4cd0bf5: R0-03B-2 still records unresolved legacy contract taxonomy debt, so this closes as PASS_WITH_WARNINGS.
- 1a48f6f3fb76: R0-05 deliberately leaves evidence ledger persistence, review queue persistence, and public index rebuild for later tasks.
- 1a48f6f3fb76: R0-05 deliberately leaves evidence ledger persistence, review queue persistence, and public index rebuild for later tasks.
- 1a48f6f3fb76: R0-05 deliberately leaves evidence ledger persistence, review queue persistence, and public index rebuild for later tasks.
- a9c536dfe1f9: R0-06 deliberately leaves review queue persistence and public index rebuild for later tasks.

## Follow-up

- 5f5e5bcb22d2: Run R0-03C to resolve remaining contract taxonomy blockers before R0-04.
- 5f5e5bcb22d2: Run R0-03C to resolve remaining contract taxonomy blockers before R0-04.
- 5f5e5bcb22d2: Run R0-03C to resolve remaining contract taxonomy blockers before R0-04.
- 5f5e5bcb22d2: Run R0-03C to resolve remaining contract taxonomy blockers before R0-04.
- 8bb9e4cd0bf5: R0-05 should add the durable source cache store. F0 and dev-to-main promotion remain blocked.
- 8bb9e4cd0bf5: R0-05 should add the durable source cache store. F0 and dev-to-main promotion remain blocked.
- 1a48f6f3fb76: R0-06 should add the durable evidence ledger store.
- 1a48f6f3fb76: R0-06 should add the durable evidence ledger store.
- 1a48f6f3fb76: R0-06 should add the durable evidence ledger store.
- a9c536dfe1f9: R0-07 should add the review queue product seam.

## Warnings

- None.

## Preview Caveat

- This draft is not an official release note and does not create tags or GitHub Releases.
