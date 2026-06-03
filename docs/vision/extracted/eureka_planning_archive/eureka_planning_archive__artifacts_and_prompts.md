# Artifacts and Prompts — Eureka Planning, AIDE Control, Local Appliance, and Search Hunt Workbench

## AIDE Lite handoff artifacts

Type: repo-local control artifacts, reported by user.

Purpose: Make Eureka self-sufficient for AIDE Lite / Codex work.

Contents: The user reported `.aide/queue/EUREKA-AIDE-FINAL-HANDOFF-01/`, `.aide/reports/eureka-aide-lite-operating-handoff.md`, `.aide/queue/index.yaml`, AGENTS.md updates, and refreshed AIDE context/task/review/eval/routing/token/memory artifacts.

Status: Reported PASS by the user; not created by this assistant in this chat.

Preserve: yes.

Future use: Supports future task packets, review packets, and Codex prompt discipline.

Caveat: AIDE state can become stale after branch movement.

## `EUREKA-AIDE-REAL-01 — Add Eureka AIDE Lite repo-health report`

Type: Codex prompt generated in this chat; later reported executed by user.

Purpose: Add compact repo-health Markdown and JSON reports and prove the AIDE Lite handoff works on a real bounded task.

Contents: The prompt required `.aide/reports/eureka-repo-health.md`, `.aide/reports/eureka-repo-health.json`, validation summaries, product-boundary statements, next execution spine, and future-agent read order.

Status: User reported PASS with commit `5f57af5 docs(aide): add eureka repo health report`.

Preserve: yes.

Future use: Shows the early operationalization of AIDE Lite in Eureka.

Caveat: Later repo-health claims may become stale.

## `EUREKA-CONVERGE-01 — Track and prompt queue convergence audit`

Type: Codex prompt generated in this chat.

Purpose: Reconcile repo state, AIDE queue state, old P-number prompt plan, and new Track A/B/D/C/E order.

Contents: The prompt required `control/audits/eureka-convergence-v0/` and possible roadmap/ADR updates.

Status: Prompt generated; execution result was not explicitly shown in the chat.

Preserve: yes.

Future use: Important transitional artifact from AIDE sync into Eureka track execution.

Caveat: Later branch-state plans supersede it as immediate current work.

## Track A/B/D/C/E planning artifacts

Type: roadmap/planning content discussed in chat.

Purpose: Structure the project into representation/view-model spine, node/contribution network, snapshot/relay, native clients, and hosting/ops.

Contents: Track prompt lists, deliverables, exit gates, forbidden actions, and rationale.

Status: Planning doctrine; later user messages imply Track A and B were completed enough, but this chat does not fully verify every implementation detail.

Preserve: yes.

Future use: Useful for book chapters and historical architecture.

Caveat: Current execution queue has moved beyond some of these tracks.

## Native monorepo structure

Type: directory architecture proposal accepted in planning.

Purpose: Organize native clients by stable API/toolchain family.

Contents: `native/mac/carbon`, `native/mac/appkit`, `native/mac/swiftui`, `native/win/win16`, `native/win/win32`, `native/win/winforms`, `native/win/winui`, plus `native/lib/c89`, `native/lib/objc`, `native/lib/dotnet`, and matrix files.

Status: Planning decision; not verified as implemented in this chat.

Preserve: yes.

Future use: Native-client chapter/spec.

Caveat: Native work remains later.

## Local Appliance / Workbench plan

Type: product-kernel plan.

Purpose: Make Eureka runnable locally before extraction/source/ranking expansion.

Contents: LOCAL-00 through LOCAL-14, including instance bootstrap, HTTP server, HTML workbench, WorkUnit queue, review/rebuild, worker runner, auto-test harness, LAN policy, clean-machine proof, and closeout.

Status: Later GitHub queue output showed LOCAL-00 through LOCAL-14 completed on `dev`.

Preserve: yes.

Future use: Central to current architecture.

Caveat: Main/dev branch divergence means promotion and exact state need reconciliation.

## Search Hunt / HUNT artifacts

Type: runtime/product track and audit artifacts.

Purpose: Convert search into resumable investigation.

Contents: HUNT-00 through HUNT-12, Search Hunt Sessions, UI state, pause/resume/steer commands, exhaustion reports, hunt-to-SearchNeed, hunt-to-WorkUnit, background runner, workbench smoke, agent research contract, replay, disabled AI gate, closeout.

Status: GitHub connector output showed dev queue entries completed; HUNT closeout file said pass_with_warnings with zero hard blockers and six warnings.

Preserve: yes.

Future use: Core product narrative and future SYN/F0 foundation.

Caveat: Needs post-sync closeout and promotion review.

## `SYN-00 — Synthetic Query Foundry planning over Local Appliance`

Type: queued task on dev.

Purpose: Plan synthetic query/eval pressure after HUNT.

Contents: Dev task packet says SYN should create query and eval pressure before extraction/source expansion resumes.

Status: Queued, not yet executed in this chat.

Preserve: yes.

Future use: Next product phase after branch sync and HUNT closeout.

Caveat: Should not start before sync/promotion review per final recommendation.

## GitHub branch comparison output

Type: live repo-state evidence from GitHub connector in this chat.

Purpose: Verify `main` and `dev` state.

Contents: Compared `main` and `dev`, reporting diverged status, ahead_by 13, behind_by 13, main head, merge base, and extensive file list.

Status: Current within this chat at time of tool call; may become stale later.

Preserve: yes.

Future use: Source trail for why branch sync became the next action.

Caveat: Time-sensitive.

## Main task packet and golden-task reports

Type: GitHub connector outputs.

Purpose: Show current `main` control state and AIDE eval debt.

Contents: Main latest task packet points to Q62; main golden tasks fail 9 of 136.

Status: Verified in chat.

Preserve: yes.

Future use: Supports `AIDE-EVAL-GREEN-01`.

Caveat: Could change after next repo update.

## Dev task packet, health, queue, HUNT closeout, and warning disposition

Type: GitHub connector outputs.

Purpose: Show current `dev` HUNT/SYN state.

Contents: Dev latest task packet points to SYN-00; health says HUNT-12 completed with warnings; HUNT closeout says complete with zero hard blockers; warning disposition lists six warning classes; queue shows LOCAL/HUNT completed and SYN queued.

Status: Verified in chat.

Preserve: yes.

Future use: Supports post-sync HUNT closeout and SYN readiness.

Caveat: Time-sensitive.

## Archive package created by this response

Type: generated archive files.

Purpose: Preserve this chat for future project book, aggregation, and source tracing.

Contents: Seven Markdown files and a ZIP package.

Status: Created in this assistant response.

Preserve: yes.

Future use: Main source for future aggregation of this chat.

Caveat: Based only on visible chat contents and tool outputs from this chat.
