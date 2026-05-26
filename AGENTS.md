# Eureka Repo Identity

- Project name: Eureka
- Canonical short namespace: `eureka`
- Repo state: bootstrap and pre-product

## Core Doctrine

- Plan first for any non-trivial task. Inspect the relevant paths, write a bounded plan, and update it as the work changes.
- Respect boundaries. Edit only the paths needed for the task and preserve the contract split between control, contracts, runtime, and surfaces.
- Verify before claiming completion. Run the lightweight checks that fit the scope and report what was actually verified.
- Use `control/inventory/tests/command_matrix.json` and `docs/operations/TEST_AND_EVAL_LANES.md` when choosing verification lanes for larger tasks.
- State blocked and deferred items explicitly. Do not imply completion by silence when something was left open on purpose.
- Treat placeholders honestly. Do not fabricate mature behavior, stable semantics, or fake completeness.

## High-Level Component Boundaries

- `control/` holds governance and planning material, not product runtime behavior.
- `contracts/` holds governed schemas, protocols, public API contracts, and shared UI contracts.
- `runtime/engine` owns engine behavior plus the concrete interface boundaries under `runtime/engine/interfaces/`.
- `runtime/gateway` owns gateway-facing runtime behavior and depends on contracts plus `runtime/engine/interfaces/public/**` and `runtime/engine/interfaces/service/**`.
- `runtime/connectors` implements bounded acquisition adapters and may depend only on `runtime/engine/interfaces/ingest/**`, `runtime/engine/interfaces/extract/**`, and `runtime/engine/interfaces/normalize/**` plus governed archive contracts.
- `surfaces/web` and `surfaces/native` are user-facing surfaces.
- `.aide/` owns repo operating metadata only.

## Dependency Law

- Web uses gateway public APIs and contracts in the normal path.
- Native uses contracts and gateway public APIs in the normal path.
- Native may use `runtime/engine/sdk` only if an explicit offline or local mode is deliberately adopted later.
- Gateway may depend only on `runtime/engine/interfaces/public/**`, `runtime/engine/interfaces/service/**`, and governed contract paths.
- Connectors may depend only on `runtime/engine/interfaces/ingest/**`, `runtime/engine/interfaces/extract/**`, `runtime/engine/interfaces/normalize/**`, and governed archive contract paths.
- Engine must not depend on `surfaces/*`.
- Web must not depend on engine internals in the normal path.
- Connectors must not invent object truth.
- Connectors must not own trust semantics.
- AIDE does not own product semantics and must not define runtime behavior.

## Working Rules for Agents

- Before starting normal Codex/AIDE task work, run the Git task-state guard:
  `python scripts/check_git_task_state.py --mode start-task --task-id <task-id>`.
  Do not start normal work on a dirty tree, active merge/rebase/cherry-pick,
  stale `main`, or direct `main`. Use `AIDE-SYNC-01`, `AIDE-MERGE-01`, or
  `AIDE-RESCUE-01` for multi-machine sync, integration, and rescue workflows.
- For non-trivial Eureka work, read `.aide/context/latest-task-packet.md` first and use `.aide/reports/eureka-aide-lite-operating-handoff.md` as the AIDE operating reference.
- Keep changes narrowly scoped to the requested boundary.
- Prefer governed contract edits over hidden coupling.
- When a task crosses component boundaries, name the boundary crossing in the plan and in the final report.
- Run `python scripts/check_architecture_boundaries.py` when Python-layering changes could affect runtime, gateway, connector, or surface boundaries.
- If verification cannot be completed, say so plainly and list the reason.
- If follow-up work is intentionally deferred, list it under a clear deferred or open-items heading.
- Repo audits should emit structured findings under `control/audits/` and should not be treated as production-readiness claims.
- AIDE Lite supports repo governance and context compression; it is not product truth. Product truth lives in `contracts/`, `runtime/`, and accepted architecture docs.
- AIDE-only tasks must not modify product behavior. Write evidence under `.aide/queue/<TASK-ID>/` and do not paste full chat history when a compact task packet exists.
- Use structured Markdown commit bodies for substantive work; run `py -3 .aide/scripts/aide_lite.py commit check --latest` after committing when practical.
- If prompts repeat, arrive out of order, or interrupt incomplete work, resume from repo-local queue/status/evidence first. Reconcile repeated or out-of-order prompts before editing, and ask the user only after repo-local evidence is insufficient to choose a safe continuation.

## Long-Test Token Discipline

Agents must not stream repeated progress updates while long-running validation
commands execute.

For commands expected to exceed 120 seconds:

1. Run the command through a repo-local harness or CI.
2. Capture stdout/stderr to files.
3. Produce a compact JSON summary.
4. Report only the summary.
5. Do not poll repeatedly in chat unless the user explicitly asks.

Full unittest discovery is a promotion/nightly/manual gate, not a normal
per-edit validation step. During AI-assisted work, use focused lanes selected
by `scripts/eureka_test_select.py --changed --failed-first --json` unless the
task explicitly requires promotion validation.

Full unittest discovery must not run inside AI sessions by default. If full
discovery is required, write `external_full_discovery_handoff.json`, stop with
`WAITING_FOR_EXTERNAL_FULL_DISCOVERY`, and resume only after an operator or CI
returns `full_unittest_summary.json`. Do not paste full logs into the AI
session; request targeted traceback excerpts only when the compact summary is
insufficient.

<!-- AIDE-PORTABLE:BEGIN section=aide-lite-pack-v0 mode=managed -->
## AIDE Lite Portable Guidance

- This repository uses a portable AIDE Lite Pack imported from AIDE.
- Keep target-specific project state in `.aide/memory/`; do not copy source AIDE memory.
- Do not copy source `.aide/queue/`, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, `.aide.local/`, raw prompts, raw responses, or secrets.
- Generate target-local context with `py -3 .aide/scripts/aide_lite.py snapshot`, `index`, `context`, and `pack`.
- Use `py -3 .aide/scripts/aide_lite.py test` for portable AIDE Lite validation.
- Provider/model/network calls and Gateway forwarding remain forbidden unless a future reviewed target queue item enables them.
<!-- AIDE-PORTABLE:END section=aide-lite-pack-v0 -->

<!-- AIDE-GENERATED:BEGIN section=aide-token-survival-adapter target=codex_agents_md generator=aide-adapter-compiler-v0 version=q24.existing-tool-adapter-compiler.v0 source_template=.aide/adapters/templates/AGENTS.md.template mode=managed_section manual=outside-only fingerprint=sha256:8f573bef168a6f16af88c7aef03c771d113a5971324cafb15f8b8bed4374c597 -->
## AIDE Existing-Tool Adapter: Codex

- Use `.aide/context/latest-task-packet.md` as the default task brief.
- Use `.aide/context/latest-context-packet.md` for compact repo refs when the
  task packet points there.
- Do not paste long chat history, full repo dumps, raw prompts, raw responses,
  secrets, provider keys, or `.aide.local/` contents.
- Prefer exact repo refs and line refs over copied file bodies.
- Before substantive work, run `py -3 .aide/scripts/aide_lite.py doctor`,
  `validate`, and `pack --task "<bounded task>"` when available.
- For quality-sensitive work, run `verify`, `review-pack`, `eval run`, and
  evidence checks before review or promotion.
- For Q27-and-later work, use structured commits and run `commit check` when
  practical.
- Inspect `task status` or `task inspect` before repeated, partial, or
  out-of-order queue work.
- Run `git plan` before branch-sensitive work; do not mutate branches without
  an explicit helper plan, validation evidence, and operator approval.
- Treat Gateway and provider surfaces as no-call/report-only unless a future
  reviewed queue phase explicitly enables live execution.
- Write evidence, preserve manual content, stop at review gates, and report
  validation honestly.
<!-- AIDE-GENERATED:END section=aide-token-survival-adapter -->
