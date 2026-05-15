# Capability Map

| Capability | Existing tool candidates | Status | Future AIDE wrapper |
|---|---:|---|---|
| validate | 559 | Present; preserve validators | Wrap selected validators after reviewed authorization |
| test | 148 | Present; use documented lanes | Map lanes from `command_matrix.json` and `TEST_AND_EVAL_LANES.md` |
| build | 107 | Present; build-sensitive | Review-only in Q56; no build execution unless future task allows |
| audit | 484 | Present; many control audit artifacts | Wrap audit summarizers/report validators later |
| lint | Included in validation/test families where named | Not separated by current inventory | Future normalize if recurring commands are found |
| format | 14 | Present | Preserve; no formatter execution in Q56 |
| generate | 130 | Present; mutation-sensitive | Future wrappers must dry-run first |
| repo_policy | 637 including Q56 enriched tags | Present | Wrap `AGENTS.md`, command matrix, test lane policy as read-only inputs |
| architecture_policy | 139 | Present | `eureka.validate.architecture` future wrapper |
| source_policy | 446 | Present; safety-critical | Future wrapper-first strategy; no live/source mutation in Q56 |
| evidence_policy | 88 | Present; safety-critical | Future wrapper-first strategy; no evidence-ledger writes in Q56 |
| index_policy | 55 | Present; safety-critical | Future wrapper-first strategy; no public-index writes in Q56 |
| snapshot_policy | 15 | Present | Future wrapper around snapshot validators only |
| site_policy | 9 | Present | Future wrapper around site validators; no deploy/build publish in Q56 |
| connector_policy | 502 | Present; network-sensitive | Future wrapper must require explicit no-network/live-call gates |
| docs | 244 | Present | Preserve as authority/reference inputs |
| release/package | release 293; package 425 | Present; release-sensitive | No release publication; dry-run/read-only wrappers only |
| migration | Present in source/evidence/index path policies | Mutation-sensitive | No migration in Q56 |
| security | 2 | Present | Preserve; secret scan remains separate validation |
| install | 184 | Present | AIDE install/upgrade state only; no install in Q56 |
| context | 574 | Present | Generated packets and context remain evidence |
| unknown | 285 | Present | Preserve/manual review; execution_allowed false |
