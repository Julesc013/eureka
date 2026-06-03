# Current State Summary — Eureka HUNT, IA, SYN, and Artefact Resolution Planning

Date anchor: 2026-05-31 Australia/Melbourne  
Scope note: Based on visible chat content only.

## Current State in One Page

This chat leaves Eureka at a major architectural checkpoint. The project has been reframed from a scaffold-heavy search/archive project into a local-first universal artefact-resolution engine. The visible conversation says the project has passed through recovery work, Local Appliance work, HUNT search-investigation work, PLAY demo/seed work, and an Internet Archive metadata pilot on `dev`.

The most recent visible project-state claim is that `dev` contains Local Appliance + HUNT + PLAY + an IA metadata source vertical slice, and that the IA pilot is complete through reviewed local index proof. This means the described pipeline is no longer only conceptual: IA metadata has reportedly flowed through source cache, evidence candidates, provisional candidates, review/promotion dry-run, reviewed local index rebuild, and search/object/absence proof. However, this archive report does not independently verify the repository after that claim. Treat it as a visible-chat fact, not an independently audited fact.

The product direction is settled at a high level: Eureka should be a general artefact-resolution engine. It should handle old software, drivers, manuals, packages, hidden archive members, frontier-resolution media, and other hard-to-resolve objects. Its core loop is query → local reviewed index → Hunt → exhaustion report → SearchNeed → WorkUnits → source observations/evidence candidates → review → reviewed index → Resolution Packet. The project should not become a generic crawler, downloader, public search fanout, or AI answer engine.

The most important near-term product desire from the user is a local HTML page where they can type a query and see results arrive progressively: local reviewed results first, cached candidates next, bounded IA metadata results next, then item metadata and file manifests, then evidence/review/index updates, with extraction deferred. This should be built as progressive source lanes, not a synchronous “search all of IA” crawl.

The work is still not public-production-ready. The chat repeatedly preserves non-claims: no deployment, no production readiness, no public launch readiness, no unrestricted source probes, no downloads, no extraction, no model/provider execution, no master-index mutation, and no automatic truth acceptance.

## Settled Points

Eureka should remain local-first until production gates exist. The Local Appliance and HUNT workflow are the foundation for future work.

HUNT is the active search-investigation spine. Misses become Hunts, exhaustion reports, SearchNeeds, and WorkUnits rather than dead ends.

IA metadata is the first source-family wedge. It should grow from metadata-only pilot into progressive IA search lanes.

SYN should be an evaluation and query-pressure system, not a fake-data factory.

Domain packs should eventually make the engine general across software, drivers, media, manuals, packages, research objects, and more.

Source observations, synthetic outputs, and AI outputs are not truth. Review is required for promotion.

## Tentative Points

The exact operational order after IA pilot is tentative. The chat suggests IA-to-main promotion review first, then SYN or IA-DEEP. But a future assistant must verify repo state before deciding.

The placement of DOMAIN and SCOUT relative to SYN/F remains roadmap-level. The chat strongly recommends SYN foundation → DOMAIN → SCOUT → SYN integration → F, but this has not been executed.

The frontier-resolution media domain is accepted as a strong conceptual wedge, but not yet implemented as a domain pack.

## Blocked Points

Public production is blocked by missing hosting, ops, security, abuse, privacy, observability, backup/restore, takedown, source-policy enforcement, and production search-quality work.

Deep IA file/member discovery is blocked until F0 extraction gates exist.

Downloads, mirroring, install/emulate actions, and public hosted IA-backed search are blocked until later action, safety, and operations tracks.

AI research execution is blocked until K or a later AI gate. Current AI escalation is described as disabled/candidate-only.

## User Decisions Needed

The user should decide whether the next execution step is:

- IA-to-main promotion review, if `dev` has IA/PLAY/HUNT work not yet on `main`;
- IA-DEEP-00 planning, if staying on `dev` intentionally;
- or SYN-00, if IA promotion and source-pilot closeout are already canonical.

The user should decide how soon to formalize the frontier-resolution media domain pack.

The user should decide whether IA progressive search should be prioritized before SYN or interleaved with SYN.

## Verification Needed

Verify current branch state: `main`, `dev`, merge-base, ahead/behind counts.

Verify whether IA pilot work has been promoted to `main`.

Verify the latest AIDE eval, report-size, HUNT closeout, PLAY, IA closeout, and repo-health reports.

Verify which scripts and runtime paths actually exist for PLAY, IA, HUNT, and local workbench.

Verify whether full unittest discovery, generated artifact cleanliness, architecture boundaries, and runtime leakage checks pass.

## Best Next Action

If repo state matches the latest visible claim that IA pilot exists only on `dev`, run an IA-to-main promotion review. If promotion is already complete, run IA-DEEP-00 or SYN-00 depending on whether the user wants progressive IA search next or evaluation pressure next.

## Future Assistant Instructions

Do not re-ask whether Eureka should be local-first, evidence-first, or HUNT-driven; that is established in this chat. Do verify repo state before producing operational prompts. Do not treat IA metadata as truth or implement downloads/extraction/model calls prematurely. Preserve the progressive IA lane model and the universal artefact-resolution framing.
