# Current State Summary — Eureka Workbench, IA Connector, and Production Path

## Current State in One Page

As of the requested archive date anchor, 2026-05-31 Australia/Melbourne, the final visible state of this chat is a planning and status synthesis, not a fresh repository verification. The latest concrete repository state discussed in the chat was dated 2026-05-19 and should be reverified before work resumes.

The conversation ended with Eureka described as having moved beyond pure scaffolding into a real local source-backed loop. The visible chat reports that HUNT was complete, PLAY was available, and an Internet Archive metadata pilot had completed through a reviewed local index proof. The IA path was described as metadata policy, fixture replay, a bounded live metadata probe, source-cache write path, evidence candidate integration, candidate index integration, review/promotion dry-run, reviewed local index rebuild, and search/object/absence proof. At the same time, the chat repeatedly emphasized that this was not full Archive.org integration, not public hosting, not production, and not a marketplace.

The most important current design conclusion is that the Workbench should become the internal/operator superset of the final product. It should not be a throwaway admin page, a separate UI, or a temporary developer dashboard. It should use the same kernel and packets that later public web, API, CLI, native, mobile, snapshot, and relay surfaces consume. The public app should be a restricted, safe projection of the same system.

The best next sequence proposed at the end was: verify current branch state; promote the IA baseline to main if still only on `dev`; then run Workbench Foundation, Workbench Result Lanes, Workbench Events, IA-HUNT bridge, IA WorkUnit/UI/apply gate work, and then SYN over Local/HUNT/PLAY/IA. SYN remains important, but the final recommendation was that SYN should test Workbench-visible behavior rather than hidden backend state.

Public stable hosted production remains far away. The chat identified many requirements still missing or future: broader source expansion, review UI hardening, durable persistence seams, search quality/ranking/identity, extraction/member discovery, DOMAIN packs, SCOUT graph, packs/federation, safe actions, snapshots/relay, native clients, hosting operations, security, observability, backups, rollback, incident response, takedown, privacy, source terms compliance, and production governance.

## Settled Points

The Workbench should be treated as the internal superset and proving surface.

The IA connector should be progressive and reviewed, not a synchronous deep crawl of all Internet Archive while the user waits.

Candidates, source observations, synthetic outputs, and AI outputs are not truth. Review remains the promotion gate.

Public hosting, production claims, downloads, uploads, accounts, telemetry, install/execute, marketplace behavior, and public fanout remain deferred.

The project should avoid repeating the failure mode of counting contracts, examples, validators, and audit packs as product capabilities.

## Tentative Points

The exact next queue depends on current repository state. The chat recommended IA promotion before Workbench work if IA was still only on `dev`, but this is not shown as completed in the visible transcript.

The precise Workbench route list, packet names, and event model are proposals. They should be reviewed and refined before implementation.

The plan to run SYN after Workbench Foundation is a product-sequencing recommendation, not a confirmed user decision.

The long-term stable hosted production roadmap is conceptual and requires verification and decomposition.

## Blocked Points

Full public hosting is blocked by missing operations, security, privacy, rate limits, abuse controls, production index maturity, and public launch evidence.

Full Internet Archive deep indexing is blocked by policy, rate limits, review, source-cache/evidence/index architecture, extraction safety, and product UX concerns.

Marketplace/app-manager behavior is blocked by missing download, mirror, install, execute, rights, malware, quarantine, trust, rollback, and moderation systems.

Broad source expansion should be blocked until the IA/Workbench loop is visible and the source-family pattern is disciplined.

## User Decisions Needed

The user needs to decide whether to promote the IA pilot baseline from `dev` to `main` before Workbench work.

The user needs to confirm whether Workbench Foundation should take priority over SYN-00 as the next practical implementation step.

The user needs to decide how operator-only Workbench functions should be separated from future public projections.

The user needs to decide when local live source metadata probes are acceptable beyond IA.

## Verification Needed

Verify current `dev` and `main` state after 2026-05-19.

Verify whether IA-TO-MAIN-PROMOTION-REVIEW has been run.

Verify whether Workbench Foundation has already been queued or implemented outside this chat.

Verify how much of the IA vertical slice is permanent runtime versus temp-instance proof.

Verify current scripts, routes, local server, instance layout, and PLAY/IA commands before relying on them.

## Best Next Action

Recheck live repo state. If IA pilot work is still only on `dev`, run IA-TO-MAIN-PROMOTION-REVIEW. Then queue WORKBENCH-FOUNDATION-00 to define the Workbench doctrine, route/view/API matrix, shared packets, permissions, and projection model.

## Future Assistant Instructions

Do not restart the old H2/H14/F0 expansion plans unless the user explicitly asks. Do not assume public hosting or full IA integration exists. Continue from the Workbench-centered product doctrine: one kernel, many projections. Treat visible branch facts as stale until reverified. Separate user decisions from assistant recommendations. Preserve the guardrail that no candidate, synthetic output, source observation, or AI output becomes truth without review.
