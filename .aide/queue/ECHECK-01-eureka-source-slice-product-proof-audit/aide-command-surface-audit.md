# AIDE Command Surface Audit

| Family | Available | Command Run | Result | Generated Outputs | No-Apply Safe | Target-Safe | Warnings |
|---|---|---|---|---|---|---|---|
| core | yes | doctor, validate, test, selftest, verify, review-pack | PASS/WARN | context/review/verification reports | yes | yes | verify warns on cumulative dirty diff scope. |
| eval | yes | eval run | FAIL/INCOMPLETE | latest golden report exists | yes | yes | Latest recorded 127 pass / 9 fail or timeout/no stdout. |
| ledger | yes | ledger scan, ledger report | PASS | token ledger/summary | yes | yes | Two budget warnings for large eval reports. |
| intent | yes | intent validate, compile, status | PASS | latest intent/workunit packets | yes | yes | Compiled as audit-only and not safe to execute directly. |
| repo | yes | repo inventory, validate, status | PASS/WARN | repo intelligence outputs | yes | yes | 5928 unknown classifications. |
| quality | yes | quality validate, status | PASS | quality ledger/summary | yes | yes | quality ledger rerun returned no stdout in this shell; status/validate pass. |
| refactor | yes | refactor status, validate | PASS | readiness/plan artifacts | yes | yes | map-status missing, validate-map fails because no current maps exist. |
| roots | yes | roots inventory, validate, status | PASS | root inventory/classification/plan | yes | yes | Many unknown/high-risk roots preserved; no apply. |
| tools | yes | tools inventory/status/capabilities/validate | PASS or output-limited | tool inventory/classification/wrap-plan/map | yes | yes | inventory rerun was output-limited; status shows 2164 tools, execution false. |
| install | yes | install validate | PASS | install observation/plan artifacts | yes | yes | validate only; no install apply. |
| repair | yes | repair validate | PASS | repair observation/plan artifacts | yes | yes | validate only; no repair apply. |
| upgrade | yes | upgrade validate | PASS | upgrade observation/plan artifacts | yes | yes | validate only; no upgrade apply. |
| rollback | yes | rollback validate | PASS | rollback observation/plan artifacts | yes | yes | validate only; no rollback apply. |
| uninstall | yes | uninstall validate | PASS | uninstall observation/plan artifacts | yes | yes | validate only; no uninstall apply. |
| git | yes | detect, doctor, status, policy, plan | PASS/BLOCKED | workflow/helper plan | yes | yes | git plan blocked by dirty tree; no branch mutation. |
| git dry-run remote helpers | yes | sync/land/promote dry-runs | skipped | none | n/a | yes | Skipped to preserve no-network/no-branch-mutation checkpoint boundary. |
| changelog | yes | preview, validate, status | PASS | preview changelog/release notes | yes | yes | preview-only, no release publishing. |
| task | yes | inspect, status, noop-check | PASS/WARN | task status only | yes | yes | Q62 shorthand inspect missing; full Q61 packet points to exact Q62 title. |
| release | partial | release validate, status | FAIL | local release validation report | yes | yes | Target Eureka lacks release dist artifacts; no publish/tag/upload. |
| github | partial | advisory/validate | skipped | none | n/a | yes | Skipped to avoid GitHub/API/network side effects. |

Overall: AIDE is usable for local governance and validation. Release and
refactor-map failures are expected capability-surface gaps, not source-slice
product failures.
