# Current State Summary — Eureka Workbench and Internet Archive Pilot

_Date anchor used for this report: 2026-05-31 Australia/Melbourne, per user instruction._

## Current State in One Page

At the end of this chat, Eureka is best understood as a local-first artefact-resolution system with a working Local/HUNT/PLAY foundation and a completed Internet Archive metadata pilot on the active development line described by the user’s pasted task outputs. The IA pilot is the strongest concrete milestone in the visible chat. It reportedly passed through policy approval, fixture replay, bounded live metadata probing, TLS trust repair, source-cache writes, evidence-ledger candidates, provisional candidate index, review queue and promotion dry-run, reviewed local index rebuild, search/object/absence proof, and closeout.

This does not mean Eureka is a production search engine. It does not mean full Archive.org integration is complete. It does not mean the system can crawl Archive.org, download files, unpack archives, index subdirectories, run public live fanout, or host a public search service. The IA pilot is metadata-only and bounded. It proves the source-to-reviewed-local-index loop in temporary explicit instances while preserving safety boundaries.

The workbench direction is now clear. The Workbench should be the internal/operator superset of the final product — an overpowered Mission Control surface for search, Hunts, WorkUnits, sources, evidence, candidates, review, index rebuilds, SYN evals, DOMAIN packs, SCOUT trails, extraction, snapshots, relay, and operations. Public web, API, CLI/TUI, relay, native, and mobile clients should later be restricted projections over the same kernel and packets.

The next architectural missing piece is the Search Interaction Contract. This should define how a full-sentence query becomes a compiled intent, a live resolution run, result lanes, partial results, controls, feedback events, coverage reports, absence reports, and reusable memory. Without this, the Workbench risks becoming a group of pages rather than a coherent product experience.

The current best next sequence is: verify or promote the IA pilot baseline, lock repo layout/Workbench ownership rules, define Workbench Foundation, define Search Interaction, implement result lanes and events, bridge IA into HUNT, then start SYN over the real Local/HUNT/PLAY/IA behavior.

## Settled Points

The Local Appliance should be the proving ground for future work. Mutable instance state should live outside the repo, with `../instances/default` as the preferred local instance path and `../eureka-instance` retained only as an explicit legacy sibling. The Workbench should become the internal superset, not a throwaway developer dashboard. The IA metadata pilot is treated as complete through reviewed local index proof according to the visible user statuses. Live source observations are not truth; evidence candidates are not accepted evidence; candidates require review; reviewed local index is not master index. Downloads, extraction, public fanout, model/provider calls, and production hosting remain disabled.

## Tentative Points

The exact repo branch state is tentative. The chat contains user-pasted statuses saying `dev` was ahead of `origin/dev` by one commit after several tasks. Assistant messages suggested `dev` was ahead of `main`, but future work should verify Git directly. The proposed repo structure and Workbench route layout are recommendations, not yet executed. The Search Interaction packet set and Workbench Foundation sequence are conceptually accepted but not implemented in visible status reports.

## Blocked Points

Full Archive.org deep browsing is blocked by missing IA-HUNT integration, result lanes, progressive event/polling UI, scaled metadata search, item/file manifest expansion, source frontier queues, and F0 extraction. Downloads and extraction are blocked by policy and safety requirements. Public production hosting is blocked by missing ops/security/rate-limit/observability/privacy/takedown infrastructure. Native and marketplace-style apps are blocked by missing stable APIs, snapshots/relay, action policies, pack trust, and safety systems.

## User Decisions Needed

The user must decide whether to promote the IA pilot baseline to `main` before continuing major work on `dev`. The user must also decide how aggressively to pursue repo layout cleanup before Workbench implementation. A future decision will be needed on whether `../instances/default` can be mutated by operator IA-HUNT flows or whether all source writes should remain temp-instance-only until additional backup/rollback gates exist.

## Verification Needed

Verify current Git branch state. Verify whether IA-PILOT-CLOSEOUT-01 commit has been pushed and whether `main` contains it. Verify the current full unittest failure list and whether broad-lane failures remain unrelated to IA/Workbench work. Verify tracked versus untracked files before repo-structure cleanup. Verify public README and docs before making production/public claims.

## Best Next Action

Run IA-to-main promotion review or otherwise verify canonical branch state. Then begin `REPO-LAYOUT-CANON-00` or `WORKBENCH-FOUNDATION-00`, followed by `SEARCH-INTERACTION-00`. If forced to choose one product task after promotion, choose `WORKBENCH-FOUNDATION-00` plus the Search Interaction Contract rather than another source connector.

## Future Assistant Instructions

Do not re-ask whether the Workbench should be central; this chat settled that direction. Do not claim full Archive.org integration. Do not enable downloads, extraction, or public fanout. Do not treat temp-instance IA writes as operator-instance or production writes. Do not start SCOUT as a crawler or AI as truth. Preserve the IA pilot as the first source-family pattern and build future source work from the same staged policy → fixture → live probe → cache → evidence → candidate → review → reviewed index model.
