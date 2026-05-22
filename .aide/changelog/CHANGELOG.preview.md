# AIDE Changelog Preview

This file is generated from local Git history and is a preview only.

source_range: HEAD latest 50 commits
source_head: df6a6967afdb510de46651f70e21541f20b6741b
commit_count: 50
malformed_count: 0
preview_only: true
release_publishing: false

## Summary

- Added: 49
- Changed: 36
- Fixed: 12
- Docs: 12
- Tests: 22
- Internal: 15
- Follow-up: 1

## Added

- compatibility handling for historical candidate/probe/OBS references after schema moves. (5f5e5bcb22d2 refactor(r0): clean contract references)
- source observation seam behavior and audit evidence for R0-04. (8bb9e4cd0bf5 runtime(r0): add source observation seam)
- durable source cache SQLite persistence seam for R0-05. (1a48f6f3fb76 runtime(r0): add durable source cache store)
- source cache store contracts, docs, tests, validator, and audit pack. (1a48f6f3fb76 runtime(r0): add durable source cache store)
- durable evidence ledger SQLite persistence seam for R0-06. (a9c536dfe1f9 runtime(r0): add durable evidence ledger)
- evidence ledger contracts, docs, tests, validator, and audit pack. (a9c536dfe1f9 runtime(r0): add durable evidence ledger)
- durable review queue store package and governed store contracts. (0eea9c54c65a runtime(r0): add review queue store)
- init, demo, validator, docs, inventory, and audit pack for R0-07. (0eea9c54c65a runtime(r0): add review queue store)
- reviewed public index store and rebuild pipeline. (f9d7fc25f9fd runtime(r0): add reviewed public index)
- public index store schemas. (f9d7fc25f9fd runtime(r0): add reviewed public index)
- store, rebuild, search, absence, and integration tests. (f9d7fc25f9fd runtime(r0): add reviewed public index)
- reviewed public index architecture, reference, and operations docs. (f9d7fc25f9fd runtime(r0): add reviewed public index)
- one-source PyPI live metadata pipeline and audit evidence. (90695310dc30 test(r0): run one source live pipeline)
- R0-10 production recovery review evidence and scripts. (6eeae5b324a5 audit(r0): complete production recovery review)
- R0 final closeout evidence and scripts. (0da3111215d2 audit(r0): close production recovery)
- R0 contract taxonomy remediation scripts, tests, inventories, docs, and audit pack (ede77d3cb101 fix(r0): resolve contract taxonomy blockers)
- generated artifact drift policy and validation tooling. (dbc4e72ccf63 fix(r0): reconcile generated artifact drift)
- legacy leakage remediation scripts, tests, inventories, docs, and audit pack. (be01503a76b0 fix(r0): retire legacy runtime leakage debt)
- final R0 promotion review inventories, audit pack, docs, and merge plan. (4cde57bd1004 audit(r0): review dev main promotion)
- dev-to-main R0 promotion evidence and F0 start decision. (387a307d0397 audit(r0): record dev main promotion)
- Local Appliance track policies, inventories, docs, audit pack, validator, and tests. (a140304235d7 ops(local): insert appliance track before f0)
- LOCAL-01 local instance bootstrap controls and commands. (7f373983b227 ops(local): add instance bootstrap)
- local instance schema and migration policies. (9bdad0968762 ops(local): add instance migration guard)
- store manifest, migration state, schema-version inventories, audit pack, validator, migration status command, and focused tests. (9bdad0968762 ops(local): add instance migration guard)
- runtime status, composition demo, and LOCAL-03 validator scripts. (ac9f5b8de4f6 runtime(local): add appliance composition boundary)
- LOCAL-03 policies, inventories, tests, docs, queue handoff, and audit evidence. (ac9f5b8de4f6 runtime(local): add appliance composition boundary)
- runtime/local_appliance runtime composition API. (5f9ac9870626 runtime(local): add appliance composition boundary)
- runtime status, composition demo, and LOCAL-03 validator scripts. (5f9ac9870626 runtime(local): add appliance composition boundary)
- LOCAL-03 policies, inventories, tests, docs, queue handoff, and audit evidence. (5f9ac9870626 runtime(local): add appliance composition boundary)
- runtime/local_service read-only localhost service API. (15a46c118f90 runtime(local): add read only localhost service)
- local server, smoke, and LOCAL-04 validator scripts. (15a46c118f90 runtime(local): add read only localhost service)
- LOCAL-04 policies, inventories, docs, queue handoff, tests, and audit evidence. (15a46c118f90 runtime(local): add read only localhost service)
- server-rendered local workbench runtime, smoke script, validator, policies, inventories, docs, tests, and audit pack. (e0af786e11e0 surface(local): add html workbench)
- LOCAL-06 page hardening policies, inventories, validator, tests, docs, and audit pack. (fb230b12543f surface(local): harden workbench pages)
- durable local WorkUnit queue store, state machine, records, queries, and validation. (10b8beb7364a runtime(local): add workunit queue)
- WorkUnit queue CLI, demo, and validator. (10b8beb7364a runtime(local): add workunit queue)
- local operator auth, local review service, review/rebuild routes, scripts, tests, policies, inventories, docs, and audit pack. (ff941a760345 surface(local): add review rebuild loop)
- runtime/local_worker, worker runner scripts, LOCAL-09 policies, inventories, docs, tests, validator, queue handoff, and audit pack. (5488d5b29987 runtime(local): add deterministic worker runner)
- target-local Git workflow detection and helper planning reports. (3e5302ea9a36 aide(eureka): sync Git workflow policy and reports)
- Q32 final evidence and review-gate status. (1e67573e29a1 aide(eureka): record canonical governance sync evidence)
- deterministic local auto-test and auto-search harness commands. (db42e120c3f5 test(local): add auto search harness)
- machine-readable and Markdown eval reports with latency and safety posture. (db42e120c3f5 test(local): add auto search harness)
- read-only LAN safety policy package, LAN route/mutation matrices, policy check script, validator, docs, and audit pack. (285d0c4dcd4b ops(local): add lan safety gate)
- LOCAL-12 LAN smoke/probe/shutdown scripts, validator, policies, inventories, tests, docs, and audit pack. (9bddfc02d506 test(local): prove read only lan smoke)
- LOCAL-13 clean-machine scripts, validator, policies, inventories, tests, docs, and audit pack. (d3cf4ea25532 test(local): prove clean machine bootstrap)
- LOCAL-14 closeout scripts, inventories, docs, tests, audit pack, and task stubs. (e39101948499 audit(local): close appliance track)
- final green inventories and audit evidence. (736a43a5a9c5 audit(local): green appliance baseline)
- LOCAL total remediation inventories, audit evidence, and promotion gate tests. (4e9ebd7478ae fix(local): green appliance leakage and promotion gate)
- final state inventories, audit pack, future execution plan, and chat alignment packet. (7de5c8b708c2 audit(final): align state promotion and future plan)

## Changed

- active validators and tests now follow the R0 contract taxonomy for moved control schemas. (5f5e5bcb22d2 refactor(r0): clean contract references)
- R0-03B-2 validation evidence now records the final full-suite pass. (5f5e5bcb22d2 refactor(r0): clean contract references)
- contract taxonomy scanner recognizes the required evidence_candidate runtime contract as product runtime. (8bb9e4cd0bf5 runtime(r0): add source observation seam)
- contract taxonomy inventory includes the new store contracts. (1a48f6f3fb76 runtime(r0): add durable source cache store)
- contract taxonomy durable-store classification handles store contracts before preview naming signals. (a9c536dfe1f9 runtime(r0): add durable evidence ledger)
- contract taxonomy classification now treats contracts/stores as durable store contracts before task-queue filename heuristics. (0eea9c54c65a runtime(r0): add review queue store)
- integrate remote dev cleanup commit into local dev history. (ce1ab9685222 chore(dev): integrate origin dev)
- merge R0 recovery branch into dev. (9cda6e786c25 chore(dev): merge R0 recovery branch)
- refreshed exact runtime leakage allowlist hashes after reference-only path updates. (d15eb701b478 fix(r0): resolve contract taxonomy blockers)
- refreshed governed generated artifacts and R0 closeout decision evidence. (dbc4e72ccf63 fix(r0): reconcile generated artifact drift)
- quarantine legacy H-series connector prototype runtime and update references. (be01503a76b0 fix(r0): retire legacy runtime leakage debt)
- AIDE queue, task packet, review packet, and repo health now route to LOCAL-01 before F0. (a140304235d7 ops(local): insert appliance track before f0)
- queue state advances to LOCAL-02 while F0 remains deferred. (7f373983b227 ops(local): add instance bootstrap)
- init, validate, and status scripts now understand versioned instance metadata. (9bdad0968762 ops(local): add instance migration guard)
- refreshed AIDE handover evidence and compact task/review artifacts. (cf0c53a41d93 chore(aide): revalidate Q26 Eureka handover)
- local service now serves read-only HTML routes while keeping JSON API routes under /api/v1. (e0af786e11e0 surface(local): add html workbench)
- local workbench view models and pages now expose operational status, provenance, absence layers, non-claims, and unavailable capabilities. (fb230b12543f surface(local): harden workbench pages)
- local service search JSON now preserves existing result fields while adding full reviewed record fields when available. (fb230b12543f surface(local): harden workbench pages)
- local instance manifest, runtime composition, and status now include the WorkUnit queue store. (10b8beb7364a runtime(local): add workunit queue)
- LOCAL-07 policies, inventories, audit pack, leakage baseline, and queue handoff. (10b8beb7364a runtime(local): add workunit queue)
- local service and workbench routes now expose operator-gated review/rebuild pages and APIs. (ff941a760345 surface(local): add review rebuild loop)
- WorkUnit queue now records worker result and audit payload references. (5488d5b29987 runtime(local): add deterministic worker runner)
- imported canonical AIDE governance and validation tooling into Eureka. (21e4f766300d aide(eureka): sync portable commit and WorkUnit policies)
- regenerated Eureka-local AIDE packets and governance reports. (5d955486e323 aide(eureka): regenerate packets and validation evidence)
- refreshed agent guidance for structured commits, task recovery, and Git plan usage. (4c954e516a20 docs(eureka): record canonical AIDE governance sync)
- refreshed final Q32 reports and token metadata. (1e67573e29a1 aide(eureka): record canonical governance sync evidence)
- local server now requires explicit --bind-lan for all-interface bind hosts and blocks LAN unsafe routes. (285d0c4dcd4b ops(local): add lan safety gate)
- AIDE queue/context/repo-health to hand off to LOCAL-13. (9bddfc02d506 test(local): prove read only lan smoke)
- AIDE queue/context/repo-health to hand off to LOCAL-14. (d3cf4ea25532 test(local): prove clean machine bootstrap)
- AIDE queue/context/repo-health to hand off from LOCAL-14 to HUNT-00. (e39101948499 audit(local): close appliance track)
- completed LOCAL validators accept advanced queue state. (736a43a5a9c5 audit(local): green appliance baseline)
- final green evidence records one additional safe repair. (698e30097344 build(index): refresh public search artifact)
- LOCAL closeout warning and promotion evidence now reflect zero new unallowlisted leakage findings. (4e9ebd7478ae fix(local): green appliance leakage and promotion gate)
- promotion evidence now records the completed fast-forward promotion. (52a73c641d2c audit(local): record appliance promotion result)
- LOCAL-14 promotion review evidence restored to plan-only semantics. (7de5c8b708c2 audit(final): align state promotion and future plan)
- local AIDE control plane upgraded and Q56 Existing Tool Absorption packet generated. (df6a6967afdb chore(pack): sync stable control plane)

## Fixed

- preserve candidate-index historical contract path compatibility during merge. (ce1ab9685222 chore(dev): integrate origin dev)
- moved unresolved contract taxonomy artifacts to contracts/control_schemas (ede77d3cb101 fix(r0): resolve contract taxonomy blockers)
- updated active schema references and audit evidence needed by validators (ede77d3cb101 fix(r0): resolve contract taxonomy blockers)
- retired remaining contract taxonomy blockers and shims. (d15eb701b478 fix(r0): resolve contract taxonomy blockers)
- isolated static site JSON build test from site/dist. (dbc4e72ccf63 fix(r0): reconcile generated artifact drift)
- classified HTML heading tags and local-bundle fixture wording as leakage false positives. (dbc4e72ccf63 fix(r0): reconcile generated artifact drift)
- LAN client host handling is separated from service bind-host validation. (285d0c4dcd4b ops(local): add lan safety gate)
- stale IA readiness and local workbench test expectations. (736a43a5a9c5 audit(local): green appliance baseline)
- refreshed stale public search generated artifacts. (698e30097344 build(index): refresh public search artifact)
- runtime leakage path classification now treats nested product tests as test fixtures before production paths. (4e9ebd7478ae fix(local): green appliance leakage and promotion gate)
- runtime leakage term matching keeps uppercase governance tokens case-sensitive. (4e9ebd7478ae fix(local): green appliance leakage and promotion gate)
- runtime leakage glob matching handles mid-pattern ** fixture paths. (4e9ebd7478ae fix(local): green appliance leakage and promotion gate)

## Docs

- added R0 production review, dev-to-main promotion review, and F0 resumption gate notes. (6eeae5b324a5 audit(r0): complete production recovery review)
- added final closeout, limitations, F0 handoff, branch/queue, future completion, and recovered seam docs. (0da3111215d2 audit(r0): close production recovery)
- recorded generated artifact drift as a child remediation blocker. (d15eb701b478 fix(r0): resolve contract taxonomy blockers)
- branch state, rollback, and non-claim evidence. (387a307d0397 audit(r0): record dev main promotion)
- WorkUnit queue boundary, API, state machine, and runbook. (10b8beb7364a runtime(local): add workunit queue)
- recorded source-pack and baseline validation evidence. (5d31441b87f5 aide(eureka): add canonical governance sync packet)
- documented canonical AIDE governance sync for Eureka. (4c954e516a20 docs(eureka): record canonical AIDE governance sync)
- LOCAL auto-test harness, auto-search suites, report format, and runbook. (db42e120c3f5 test(local): add auto search harness)
- added LAN mode, route matrix, safety gate, operator boundary, and smoke prereq docs. (285d0c4dcd4b ops(local): add lan safety gate)
- LAN smoke test, external-client checklist, shutdown cleanup, limitations, route matrix, and service runbook updates. (9bddfc02d506 test(local): prove read only lan smoke)
- clean-machine bootstrap, smoke, external proof, reproducibility, and clean-state runbooks. (d3cf4ea25532 test(local): prove clean machine bootstrap)
- product kernel, capability map, closeout, future task gate, remaining warnings, HUNT/SYN/F0 handoff, promotion review, and post-LOCAL execution spine. (e39101948499 audit(local): close appliance track)

## Tests

- full unittest discovery passes on the final R0-03B-2 tree. (5f5e5bcb22d2 refactor(r0): clean contract references)
- review queue behavior, migration, and integration coverage. (0eea9c54c65a runtime(r0): add review queue store)
- added offline and mocked-live coverage for the one-source gate. (90695310dc30 test(r0): run one source live pipeline)
- added production review and promotion-plan operation tests. (6eeae5b324a5 audit(r0): complete production recovery review)
- added final closeout, safe repair, and future task gate tests. (0da3111215d2 audit(r0): close production recovery)
- added focused generated-artifact drift and isolation tests. (dbc4e72ccf63 fix(r0): reconcile generated artifact drift)
- promotion audit and dev-to-main merge plan operation coverage. (4cde57bd1004 audit(r0): review dev main promotion)
- merge evidence validator coverage. (387a307d0397 audit(r0): record dev main promotion)
- focused local instance bootstrap and policy tests. (7f373983b227 ops(local): add instance bootstrap)
- added LOCAL-02 migration guard and schema-version operation tests. (9bdad0968762 ops(local): add instance migration guard)
- focused runtime and operations coverage for composition, status, read-only mode, close idempotency, forbidden roots, unsupported schema fail-closed, and scripts. (ac9f5b8de4f6 runtime(local): add appliance composition boundary)
- focused runtime and operations coverage for composition, status, read-only mode, close idempotency, forbidden roots, unsupported schema fail-closed, and scripts. (5f9ac9870626 runtime(local): add appliance composition boundary)
- focused runtime and operations coverage for routes, read-only enforcement, host rejection, smoke, validator, and import hygiene. (15a46c118f90 runtime(local): add read only localhost service)
- page hardening focused tests and smoke assertions cover the new markers. (fb230b12543f surface(local): harden workbench pages)
- focused runtime and operations tests for queue behavior and scripts. (10b8beb7364a runtime(local): add workunit queue)
- added portable governance tests and golden tasks. (21e4f766300d aide(eureka): sync portable commit and WorkUnit policies)
- focused local eval runtime and operation script coverage. (db42e120c3f5 test(local): add auto search harness)
- added focused runtime and operations tests for LAN hosts, policy, service gate, and scripts. (285d0c4dcd4b ops(local): add lan safety gate)
- focused LAN smoke policy, read-only route, mutation blocking, client scope, and script tests. (9bddfc02d506 test(local): prove read only lan smoke)
- clean-machine bootstrap, smoke, and report operation tests. (d3cf4ea25532 test(local): prove clean machine bootstrap)
- LOCAL closeout, future gate, handoff, and promotion review operation tests. (e39101948499 audit(local): close appliance track)
- final-state, final-future-plan, and final-chat-alignment guard tests added. (7de5c8b708c2 audit(final): align state promotion and future plan)

## Internal

- refreshed contract taxonomy inventory for the new runtime contracts. (90695310dc30 test(r0): run one source live pipeline)
- AIDE review packet refreshed by review-pack. (4cde57bd1004 audit(r0): review dev main promotion)
- added no-call metadata status surfaces for validation. (cf0c53a41d93 chore(aide): revalidate Q26 Eureka handover)
- added Eureka-local Q32 governance sync queue state. (5d31441b87f5 aide(eureka): add canonical governance sync packet)
- preserved dry-run branch helper behavior for Q32. (3e5302ea9a36 aide(eureka): sync Git workflow policy and reports)
- refreshed token and changelog previews for Q32 evidence. (5d955486e323 aide(eureka): regenerate packets and validation evidence)
- refreshed generated eval report metadata. (4207f7863562 aide(eureka): refresh post-evidence eval report)
- LOCAL-10 audit pack, inventories, policies, leakage baseline, and queue handoff. (db42e120c3f5 test(local): add auto search harness)
- queue now points to LOCAL-12 while F0 remains deferred until LOCAL-14. (285d0c4dcd4b ops(local): add lan safety gate)
- recorded remote dev integration for fast-forward promotion eligibility. (cce1d0557579 chore(local): integrate remote dev baseline)
- repo health metadata now reflects aligned dev/main branches. (52a73c641d2c audit(local): record appliance promotion result)
- AIDE task and review packets refreshed for the active final audit task. (7de5c8b708c2 audit(final): align state promotion and future plan)
- synchronized local dev with latest origin/dev without publishing local commits. (859923086a7a chore(sync): merge origin dev into local dev)
- added Eureka AIDE stable-pack upgrade preflight evidence. (6f2698c6e109 aide(pack): preflight stable upgrade readiness)
- documented Q55 preservation, conflict, and absorption rules. (6f2698c6e109 aide(pack): preflight stable upgrade readiness)

## Follow-up

- LOCAL-04 requires leakage preflight reconciliation or explicit acceptance. (cf0c53a41d93 chore(aide): revalidate Q26 Eureka handover)

## Malformed Commits

- None.

## Release Caveat

- Preview only. No tags, GitHub Releases, branch mutation, or publishing were performed.
