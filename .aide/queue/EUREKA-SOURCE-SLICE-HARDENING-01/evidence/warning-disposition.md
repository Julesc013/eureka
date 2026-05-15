# Warning Disposition

| Warning | Classification | Disposition |
|---|---|---|
| Git task-state guard dirty tree | assigned_next | Existing Q56/Q57/Q58 local artifacts remain uncommitted; defer to coordinated multi-machine sync. |
| Local `main` behind `origin/main` | assigned_next | Do not mutate branches in Q59; handle during sync/integration phase. |
| `dev` behind/ahead `origin/dev` | assigned_next | Expected because another machine is actively pushing to `origin/dev`; no pull/push here. |
| Branch name does not include task id | harmless | Work is intentionally on local `dev` per current multi-machine plan. |
| Git index lock permission denied | blocking for commit, non-blocking for evidence | Commit cannot be created in this sandbox; Q59 git add failed before staging and evidence records the blocker. |
| AIDE verify missing `.aide/reports/eureka-source-slice-hardening.md` before reports existed | harmless | Report was written by Q59. |
| AIDE verify missing future `.aide/reports/eureka-object-absence-surface.md` | harmless | This is the expected future Q60 report path, not a Q59 output. |
| AIDE verify missing optional future `tests/runtime/test_fixture_object_absence_surface.py` | harmless | This is a Q60 optional test path, not a Q59 output. |
| AIDE verify dirty-scope warnings for Q56/Q57/Q58 artifacts | deferred_non_blocking | Pre-existing local evidence/generated artifacts; not a Q59 product-slice failure. |
| AIDE verify dirty-scope warnings for Q59 files | harmless | Active generated Q59 packet/reports are allowed by Q59. |
| AIDE verify dirty-scope warning for `native/win/winforms/src/Eureka/obj/` | assigned_next | Pre-existing untracked generated output; do not delete in Q59. |
| AIDE repo validate unknown file classifications | deferred_non_blocking | Existing repo intelligence warning; does not affect fixture slice behavior. |
| AIDE eval `compact_task_packet_golden` failure | deferred_non_blocking | Generic golden expectation conflicts with target product packet; not a fixture-loop failure. |
| AIDE eval GitHub/release bundle failures | deferred_non_blocking | Local Eureka target lacks release dist artifacts; unrelated to Q59 product hardening. |
| AIDE eval `github_report_only_golden` failure | deferred_non_blocking | AIDE golden policy issue, not a Q59 runtime behavior failure. |
| AIDE eval `repo_boundary_golden` failure | deferred_non_blocking | Golden expects product behavior not to change, but Q58/Q59 are explicitly product-slice implementation/hardening tasks. |
| Duplicate limitation text in public index record | assigned_next | Cosmetic/shape issue; Q60 object/absence surface should define cleaner view packets. |
| Q59 prompt reissued after Q60 artifacts exist | harmless | Repo-local queue state shows Q59 and Q60 already exist. Q59 was verified without rolling back the current Q61 task packet. |
| Q59-only commit no longer safely separable | deferred_non_blocking | Q60 later changed the same Q58/Q59 product/test files. Avoid staging a misleading Q59-only commit from the current mixed worktree. |

No warning is classified as blocking the Q59 fixture-loop hardening result.
