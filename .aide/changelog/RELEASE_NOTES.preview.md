# AIDE Release Notes Preview

This is a deterministic preview only. It does not publish a release.

## Added

- durable review queue store package and governed store contracts.
- init, demo, validator, docs, inventory, and audit pack for R0-07.
- reviewed public index store and rebuild pipeline.
- public index store schemas.
- store, rebuild, search, absence, and integration tests.
- reviewed public index architecture, reference, and operations docs.
- one-source PyPI live metadata pipeline and audit evidence.
- R0-10 production recovery review evidence and scripts.
- R0 final closeout evidence and scripts.
- R0 contract taxonomy remediation scripts, tests, inventories, docs, and audit pack
- generated artifact drift policy and validation tooling.
- legacy leakage remediation scripts, tests, inventories, docs, and audit pack.
- final R0 promotion review inventories, audit pack, docs, and merge plan.
- dev-to-main R0 promotion evidence and F0 start decision.
- Local Appliance track policies, inventories, docs, audit pack, validator, and tests.
- LOCAL-01 local instance bootstrap controls and commands.
- local instance schema and migration policies.
- store manifest, migration state, schema-version inventories, audit pack, validator, migration status command, and focused tests.
- runtime status, composition demo, and LOCAL-03 validator scripts.
- LOCAL-03 policies, inventories, tests, docs, queue handoff, and audit evidence.

## Changed

- contract taxonomy classification now treats contracts/stores as durable store contracts before task-queue filename heuristics.
- integrate remote dev cleanup commit into local dev history.
- merge R0 recovery branch into dev.
- refreshed exact runtime leakage allowlist hashes after reference-only path updates.
- refreshed governed generated artifacts and R0 closeout decision evidence.
- quarantine legacy H-series connector prototype runtime and update references.
- AIDE queue, task packet, review packet, and repo health now route to LOCAL-01 before F0.
- queue state advances to LOCAL-02 while F0 remains deferred.
- init, validate, and status scripts now understand versioned instance metadata.
- refreshed AIDE handover evidence and compact task/review artifacts.
- imported canonical AIDE governance and validation tooling into Eureka.

## Fixed

- preserve candidate-index historical contract path compatibility during merge.
- moved unresolved contract taxonomy artifacts to control/schemas
- updated active schema references and audit evidence needed by validators
- retired remaining contract taxonomy blockers and shims.
- isolated static site JSON build test from site/dist.
- classified HTML heading tags and local-bundle fixture wording as leakage false positives.

## Notes

- 18 malformed commits were excluded from release-note grouping.
