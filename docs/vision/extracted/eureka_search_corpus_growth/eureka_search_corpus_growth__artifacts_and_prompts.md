# Artifacts and Prompts — Eureka Search Engine: Corpus Growth, Public UX, and Resilient Search Planning

## Repository task prompts and status reports

Type: task prompts / operational handoffs.

Purpose: The chat generated and consumed many detailed Codex-style prompts for repo tasks. These prompts defined goals, allowed paths, forbidden paths, phases, validation, result shapes, audit packs, queue updates, and final response formats.

Status: Many were completed according to user status reports; others remain proposed.

Preserve: yes. They contain project policy, architecture, and sequencing logic.

Caveat: Do not treat a generated prompt as completed work unless the user later reported its completion.

## Test-token discipline and full discovery harness

Type: policy and tooling work.

Purpose: Externalize long-running full unittest discovery and avoid AI polling.

Contains: harness scripts, summarizers, validation scripts, CI workflows, AIDE/agent policy updates, progress/heartbeat improvements, and local run guidance as reported in the chat.

Status: reported complete and pushed earlier in the chat.

Preserve: yes. It defines future AI/test workflow.

Caveat: Exact files are not verified here; rely on repository inspection if needed.

## Public alpha launch/defer materials

Type: launch gate, approval gate, defer decision, deploy dry-run evidence.

Purpose: Initially prepare launch, then record why launch was deferred.

Status: launch deferred; no deployment/public launch.

Preserve: yes. It explains why later work focused on discovery/corpus growth.

## Active discovery stack prompts

Type: implementation prompts and completion reports.

Includes: Archive.org metadata candidates, query planner, candidate index, SCOUT runtime, review batch, seed batches, live metadata pilot, local apply.

Purpose: Build the machine that turns queries into candidates, review decisions, limited reviewed records, snapshots, and reassessments.

Status: many tasks reported complete.

Preserve: yes. This is the core technical evolution of the chat.

## Public search UX model and MVP

Type: UX/product architecture artifacts.

Purpose: Create no-JS, read-only public search pages over canonical view models.

Contains: home/search/object/candidate/need/source/evidence/status/no-results pages, result cards, status badges, accessibility/no-JS smoke, examples, docs, validators.

Status: reported complete.

Preserve: yes. Important for public product chapters.

## Snapshot refresh and public alpha reassessment series

Type: projection and product decision artifacts.

Purpose: Project current state into snapshot/relay/public UX and reassess launch readiness.

Status: v0 through v6 sequences are visible, with `SNAPSHOT-REFRESH-06` completed and `PUBLIC-ALPHA-REASSESS-06` proposed next.

Preserve: yes. This is the backbone of the project state timeline.

## Latest completed prompt/result pair

Type: status report.

Name: `SNAPSHOT-REFRESH-06`.

Purpose: Refresh snapshots after review batch apply.

Status: `PASS_WITH_WARNINGS`, commit `47425906`, `dev == origin/dev`, working tree clean, warning-only AIDE advisories.

Should feed aggregation/book/spec: yes. It marks the current end-state before archive.

## Proposed next prompt

Type: generated prompt, not yet completed.

Name: `PUBLIC-ALPHA-REASSESS-06`.

Purpose: Reassess alpha after review batch apply snapshot refresh.

Status: proposed only in visible chat.

Preserve: yes, but label as not executed.

## Expired uploaded files

Type: missing supporting materials.

Purpose: Some earlier uploads may have contained structure captures or reports.

Status: expired and unavailable in this chat at archive time.

Preserve: note only. Do not invent their contents.
