# AIDE Changelog Preview

source_range: HEAD~20..HEAD
commit_count: 20
release_publishing: false

## Added

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

## Changed

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
- imported canonical AIDE governance and validation tooling into Eureka. (21e4f766300d aide(eureka): sync portable commit and WorkUnit policies)

## Fixed

- preserve candidate-index historical contract path compatibility during merge. (ce1ab9685222 chore(dev): integrate origin dev)
- moved unresolved contract taxonomy artifacts to control/schemas (ede77d3cb101 fix(r0): resolve contract taxonomy blockers)
- updated active schema references and audit evidence needed by validators (ede77d3cb101 fix(r0): resolve contract taxonomy blockers)
- retired remaining contract taxonomy blockers and shims. (d15eb701b478 fix(r0): resolve contract taxonomy blockers)
- isolated static site JSON build test from site/dist. (dbc4e72ccf63 fix(r0): reconcile generated artifact drift)
- classified HTML heading tags and local-bundle fixture wording as leakage false positives. (dbc4e72ccf63 fix(r0): reconcile generated artifact drift)

## Docs

- added R0 production review, dev-to-main promotion review, and F0 resumption gate notes. (6eeae5b324a5 audit(r0): complete production recovery review)
- added final closeout, limitations, F0 handoff, branch/queue, future completion, and recovered seam docs. (0da3111215d2 audit(r0): close production recovery)
- recorded generated artifact drift as a child remediation blocker. (d15eb701b478 fix(r0): resolve contract taxonomy blockers)
- branch state, rollback, and non-claim evidence. (387a307d0397 audit(r0): record dev main promotion)
- recorded source-pack and baseline validation evidence. (5d31441b87f5 aide(eureka): add canonical governance sync packet)

## Tests

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
- added portable governance tests and golden tasks. (21e4f766300d aide(eureka): sync portable commit and WorkUnit policies)

## Internal

- refreshed contract taxonomy inventory for the new runtime contracts. (90695310dc30 test(r0): run one source live pipeline)
- AIDE review packet refreshed by review-pack. (4cde57bd1004 audit(r0): review dev main promotion)
- added no-call metadata status surfaces for validation. (cf0c53a41d93 chore(aide): revalidate Q26 Eureka handover)
- added Eureka-local Q32 governance sync queue state. (5d31441b87f5 aide(eureka): add canonical governance sync packet)

## Follow-up

- LOCAL-04 requires leakage preflight reconciliation or explicit acceptance. (cf0c53a41d93 chore(aide): revalidate Q26 Eureka handover)

## Malformed Commits

- 0eea9c54c65a runtime(r0): add review queue store: commit type is allowed: runtime; commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- ce1ab9685222 chore(dev): integrate origin dev: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 9cda6e786c25 chore(dev): merge R0 recovery branch: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- f9d7fc25f9fd runtime(r0): add reviewed public index: commit type is allowed: runtime; commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 90695310dc30 test(r0): run one source live pipeline: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 6eeae5b324a5 audit(r0): complete production recovery review: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 0da3111215d2 audit(r0): close production recovery: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- ede77d3cb101 fix(r0): resolve contract taxonomy blockers: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- d15eb701b478 fix(r0): resolve contract taxonomy blockers: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- dbc4e72ccf63 fix(r0): reconcile generated artifact drift: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- be01503a76b0 fix(r0): retire legacy runtime leakage debt: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 4cde57bd1004 audit(r0): review dev main promotion: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 387a307d0397 audit(r0): record dev main promotion: commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- a140304235d7 ops(local): insert appliance track before f0: commit type is allowed: ops; commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 7f373983b227 ops(local): add instance bootstrap: commit type is allowed: ops; commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- 9bdad0968762 ops(local): add instance migration guard: commit type is allowed: ops; commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- ac9f5b8de4f6 runtime(local): add appliance composition boundary: commit type is allowed: runtime; commit trailer present: AIDE-Task; commit trailer present: AIDE-Phase; commit trailer present: AIDE-Result; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact; commit trailer present: AIDE-Quality-Gate
- cf0c53a41d93 chore(aide): revalidate Q26 Eureka handover: commit trailer present: AIDE-Token-Impact
