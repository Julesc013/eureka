# Warning Disposition Audit

| Source | Warning | Classification | Blocking? | Assigned To |
|---|---|---|---|---|
| Git guard | dirty worktree with cumulative Q56-Q61 files | assigned_next | no for audit, yes for normal product start | future sync/integration review |
| Git guard | local main behind origin/main | assigned_next | no for audit | future sync/integration review |
| Git guard | dev ahead/behind origin/dev | assigned_next | no for audit | future sync/integration review |
| Git guard | branch name does not include task id | harmless | no | none |
| Git status | untracked native `obj/` output | assigned_next | no | future cleanup/rescue task |
| Q54/Q55 | source AIDE pack was preview/no-publish | expected_target_specific | no | none |
| Q55/current | target-local release dist absent | deferred_non_blocking | no | future release task only |
| AIDE eval | latest eval has 9 golden failures or timeout/no stdout | deferred_non_blocking | no for product slice | future AIDE eval hardening |
| AIDE verify | diff-scope warnings for cumulative local artifacts | expected_generated_state | no | none |
| AIDE repo | 5928 unknown file classifications | deferred_non_blocking | no | future repo-intelligence pass |
| AIDE quality | many warn-level quality candidates | deferred_non_blocking | no | future quality work |
| AIDE quality | `quality ledger` rerun produced no stdout in this shell | unknown_needs_review | no for product slice | future AIDE command audit |
| AIDE tools | `tools inventory` rerun output-limited/no stdout in this shell | deferred_non_blocking | no | future AIDE command audit |
| AIDE refactor | current move/salvage/path-alias maps missing | deferred_non_blocking | no | future refactor-map task |
| AIDE release | release validate/status fail | deferred_non_blocking | no | future release task |
| Q58-Q61 | no isolated commits for product slice | assigned_next | no for audit | future git integration/sync review |
| Q58-Q61 | duplicate limitation text in records | fixture_only | no | future surface polish |
| Q58-Q61 | source behavior remains fixture-only | fixture_only | no | Q62 or later |
| Q58-Q61 | public index is evidence-local only | fixture_only | no | later promotion task |
| Q58-Q61 | review decision is deterministic fixture review | fixture_only | no | later review workflow task |
| Q58-Q61 | object/absence packets are local runtime packets, not hosted API/UI | fixture_only | no | later API/static renderer task |
| ECHECK | GitHub advisory skipped | harmless | no | none |
| ECHECK | git sync/land/promote dry-runs skipped | harmless | no | none |
| Secret scan | 3697 policy/test/task-text matches | harmless | no | none |
| Optional Dominium read-only | sibling Dominium dirty | deferred_non_blocking | no for Eureka | XCHECK/DCHECK review |

Summary counts:

- harmless: 4
- fixture_only: 5
- expected_target_specific: 1
- expected_generated_state: 1
- deferred_non_blocking: 8
- assigned_next: 5
- blocking: 0
- unknown_needs_review: 1

No warning blocks ECHECK-01 product proof. The one `unknown_needs_review`
warning is limited to an AIDE quality ledger command rerun with no stdout; other
quality commands passed.
