# Aggregation Packet — Eureka Workbench and Internet Archive Pilot

_Date anchor used for this report: 2026-05-31 Australia/Melbourne, per user instruction._

## One-Paragraph Summary

This chat records a major convergence point in the Eureka project: the user pushed the system from broad plans into a local-first Workbench architecture with HUNT, PLAY, and a completed Internet Archive metadata pilot on `dev`. The visible task reports say IA metadata now flows through policy, fixtures, bounded live probe, TLS repair, source cache, evidence candidates, provisional candidates, review queue, promotion preview, reviewed local index, and search/object/absence proof, with no raw response, downloads, extraction, model calls, public fanout, production deployment, or master-index mutation. The chat’s main architectural decision is that the Workbench should become the internal superset of the final system, while public web/API/native clients should be restricted projections over the same kernel. The next important work is IA/main promotion review, repo layout canon, Workbench Foundation, Search Interaction Contract, result lanes/events, IA-HUNT bridge, then SYN.

## Main Themes

- Workbench as internal/operator superset of the final product.
- Search as live investigation rather than one-shot lookup.
- Internet Archive metadata pilot as the first complete source-family vertical slice.
- Evidence-first, review-gated source integration.
- Local instance separation from repo source.
- PLAY as local product legibility and smoke pressure.
- Repo structure as ownership governance, not cosmetic cleanup.
- SCOUT as relation discovery, not popularity or crawling.
- SYN as eval pressure, not fake truth.
- Full Archive.org, extraction, public hosting, native, and marketplace apps deferred.

## Major Decisions

- Local Appliance / Workbench is the execution harness.
- Mutable local instance state belongs beside the repo, not inside it.
- PLAY should provide demo/query/smoke anchors before broader source or SYN work.
- IA metadata is the first real source pilot.
- IA metadata pilot is not full Archive.org integration.
- TLS verification must not be bypassed.
- Workbench should be the internal superset; public/native surfaces are projections.
- Search Interaction Contract is required before serious Workbench/IA-HUNT/SYN product work.
- Repo layout should be locked by contracts and validators before large moves.

## Major Open Questions

- Has IA pilot closeout been promoted from `dev` to `main`?
- What are the remaining broad-lane full-discovery failures and do they block promotion?
- What is the exact Workbench route/view/permission matrix?
- What are the exact Search Interaction packet schemas and state machine?
- When can writes to `../instances/default` be safely enabled?
- How soon should IA-HUNT bridge precede SYN?
- How aggressively should repo structure be refactored before Workbench implementation?

## Major Artifacts

- LOCAL track prompts and closeout statuses.
- HUNT track prompts and closeout/promotion statuses.
- PLAY-00/01/02 prompts and status reports.
- IA-00 through IA-07 prompts and status reports.
- IA TLS trust diagnostics/repair prompts.
- IA-PILOT-CLOSEOUT-01 status.
- Repo Structure Canon Handoff Prompt.
- Uploaded current directory tree.
- Archillect/SCOUT conceptual design.
- Advanced-format media / frontier-resolution media domain discussion.

## Major Source Blocks

- The Workbench as the Internal Superset.
- One Kernel, Many Projections.
- IA Metadata Pilot as the First Source Vertical Slice.
- Metadata Is Not Truth.
- Search as Investigation.
- The Search Interaction Contract.
- Do Not Search All Archive.org Synchronously.
- TLS Verification Must Stay Enabled.
- PLAY as Product Legibility.
- Repo Structure Is Governance, Not Cosmetics.
- SCOUT as Evidence Discovery, Not Popularity.
- Full IA Integration Remains Future Work.

## Likely Overlap With Other Chats

This chat likely overlaps with earlier Local Appliance planning, HUNT implementation, AIDE branch reconciliation, repo-layout discussions, Internet Archive connector planning, SYN planning, SCOUT/Archillect discussions, and advanced-format media/domain-pack discussions.

## Likely Conflicts With Other Chats

Older chats may place F0 extraction or H-source expansion earlier. This chat supersedes that by prioritising Local/HUNT/PLAY/IA, then Workbench Foundation/Search Interaction, then SYN. Older chats may claim main/dev alignment or different branch states; verify current Git before merging.

## What To Preserve In A Master Book

Preserve the story of moving from architecture to local proof, the staged IA pilot, the Workbench-as-superset decision, and the distinction between metadata pilot and full IA integration. Preserve the safety model and non-claims.

## What Not To Assume

Do not assume IA pilot is on `main`. Do not assume full Archive.org integration. Do not assume production readiness. Do not assume public hosting or native clients are close. Do not assume repo tree in uploaded `tree` output is tracked source.

## Recommended Merge Handling

Merge this chat as a major project-state chapter. Treat pasted task statuses as FACT within this chat but verify externally before updating live project truth. Use the report for architecture/rationale, and use Git/validators for operational truth.
