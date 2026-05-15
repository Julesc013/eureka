# AIDE Changelog Preview

source_range: HEAD~20..HEAD
commit_count: 20
release_publishing: false

## Added

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

## Fixed

- LAN client host handling is separated from service bind-host validation. (285d0c4dcd4b ops(local): add lan safety gate)
- stale IA readiness and local workbench test expectations. (736a43a5a9c5 audit(local): green appliance baseline)
- refreshed stale public search generated artifacts. (698e30097344 build(index): refresh public search artifact)
- runtime leakage path classification now treats nested product tests as test fixtures before production paths. (4e9ebd7478ae fix(local): green appliance leakage and promotion gate)
- runtime leakage term matching keeps uppercase governance tokens case-sensitive. (4e9ebd7478ae fix(local): green appliance leakage and promotion gate)
- runtime leakage glob matching handles mid-pattern ** fixture paths. (4e9ebd7478ae fix(local): green appliance leakage and promotion gate)

## Docs

- recorded source-pack and baseline validation evidence. (5d31441b87f5 aide(eureka): add canonical governance sync packet)
- documented canonical AIDE governance sync for Eureka. (4c954e516a20 docs(eureka): record canonical AIDE governance sync)
- LOCAL auto-test harness, auto-search suites, report format, and runbook. (db42e120c3f5 test(local): add auto search harness)
- added LAN mode, route matrix, safety gate, operator boundary, and smoke prereq docs. (285d0c4dcd4b ops(local): add lan safety gate)
- LAN smoke test, external-client checklist, shutdown cleanup, limitations, route matrix, and service runbook updates. (9bddfc02d506 test(local): prove read only lan smoke)
- clean-machine bootstrap, smoke, external proof, reproducibility, and clean-state runbooks. (d3cf4ea25532 test(local): prove clean machine bootstrap)
- product kernel, capability map, closeout, future task gate, remaining warnings, HUNT/SYN/F0 handoff, promotion review, and post-LOCAL execution spine. (e39101948499 audit(local): close appliance track)

## Tests

- added portable governance tests and golden tasks. (21e4f766300d aide(eureka): sync portable commit and WorkUnit policies)
- focused local eval runtime and operation script coverage. (db42e120c3f5 test(local): add auto search harness)
- added focused runtime and operations tests for LAN hosts, policy, service gate, and scripts. (285d0c4dcd4b ops(local): add lan safety gate)
- focused LAN smoke policy, read-only route, mutation blocking, client scope, and script tests. (9bddfc02d506 test(local): prove read only lan smoke)
- clean-machine bootstrap, smoke, and report operation tests. (d3cf4ea25532 test(local): prove clean machine bootstrap)
- LOCAL closeout, future gate, handoff, and promotion review operation tests. (e39101948499 audit(local): close appliance track)
- final-state, final-future-plan, and final-chat-alignment guard tests added. (7de5c8b708c2 audit(final): align state promotion and future plan)

## Internal

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

## Malformed Commits

- 5488d5b29987 runtime(local): add deterministic worker runner: commit type is allowed: runtime; commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- db42e120c3f5 test(local): add auto search harness: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 285d0c4dcd4b ops(local): add lan safety gate: commit type is allowed: ops; commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 9bddfc02d506 test(local): prove read only lan smoke: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- d3cf4ea25532 test(local): prove clean machine bootstrap: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- e39101948499 audit(local): close appliance track: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 736a43a5a9c5 audit(local): green appliance baseline: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 698e30097344 build(index): refresh public search artifact: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 4e9ebd7478ae fix(local): green appliance leakage and promotion gate: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- cce1d0557579 chore(local): integrate remote dev baseline: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 52a73c641d2c audit(local): record appliance promotion result: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 7de5c8b708c2 audit(final): align state promotion and future plan: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
