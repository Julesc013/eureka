# Source Blocks for Future Book — Eureka Workbench and Internet Archive Pilot

_Date anchor used for this report: 2026-05-31 Australia/Melbourne, per user instruction._

## Block 1 — The Workbench as the Internal Superset

Type:
- decision / rationale

Source status:
- FACT for the user’s stated preference; INFERENCE for how it should be formalized.

Text:
The user stated that the Workbench should not be “just any old developer tool,” but should be built as if it were the final system: an overpowered admin/developer version of the websites and apps, so backend and frontend bugs are worked out before deployment.

Why this block matters:
This is the clearest statement of the Workbench’s role. It should anchor future product and repo-structure decisions.

Suggested future chapter/theme:
- Workbench as Mission Control
- Internal Superset and Public Projection

## Block 2 — One Kernel, Many Projections

Type:
- explanation / design logic

Source status:
- INFERENCE accepted in conversation, not yet implemented.

Text:
The recommended architecture is one Eureka kernel with many projections: Workbench, public web, API, CLI/TUI, relay/snapshot clients, native clients, and mobile later. Different permissions and display density, same semantics.

Why this block matters:
It prevents future forks between admin UI, public website, and native clients.

Suggested future chapter/theme:
- Product Surface Architecture

## Block 3 — IA Metadata Pilot as the First Source Vertical Slice

Type:
- factual status summary

Source status:
- FACT as a user-pasted task status, subject to Git verification.

Text:
The IA metadata pilot reportedly completed through IA-07 and closeout: policy, fixture replay, bounded live metadata probe, TLS repair, source cache, evidence candidates, provisional candidates, review queue, promotion dry-run, reviewed local index rebuild, and search/object/absence proof.

Why this block matters:
This is the chat’s concrete engineering milestone. It should be preserved as the first source-family pattern.

Suggested future chapter/theme:
- Evidence-First Source Connectors
- Internet Archive Metadata Pilot

## Block 4 — Metadata Is Not Truth

Type:
- rationale / constraint

Source status:
- FACT as repeated visible doctrine in the chat.

Text:
IA metadata is source observation material, not truth. Source cache records are observations; evidence ledger records are claim candidates; candidate index records are provisional; review decisions and reviewed local records do not become master-index truth automatically.

Why this block matters:
This boundary prevents future assistants or tools from corrupting the index by treating source metadata as verified fact.

Suggested future chapter/theme:
- Review Gates and Truth Boundaries

## Block 5 — Search as Investigation

Type:
- explanation / product philosophy

Source status:
- FACT as repeated plan content; implementation remains partial.

Text:
Search should not be just query → results. In Eureka, a search should become a resolution run: local results, absence/near misses, Hunts, WorkUnits, source cache, evidence, provisional candidates, review, promotion, and reusable memory.

Why this block matters:
This is one of the core product concepts.

Suggested future chapter/theme:
- Search as Investigation

## Block 6 — The Search Interaction Contract

Type:
- next step / unresolved design requirement

Source status:
- INFERENCE / accepted recommendation.

Text:
The chat identified Search Interaction Contract as the missing explicit layer: full-sentence query, compiled intent, ResolutionRun, result lanes, user controls, feedback events, coverage reports, absence reports, and discovery trails.

Why this block matters:
It defines the next major architectural task after IA and Workbench foundation.

Suggested future chapter/theme:
- Interactive Search Semantics

## Block 7 — Do Not Search All Archive.org Synchronously

Type:
- rejection / design constraint

Source status:
- FACT as a visible recommendation; external technical assumptions should be verified when implemented.

Text:
The chat rejected “one request searches all of Archive.org deeply while the user waits.” The preferred design is progressive: local index first, cached candidates, bounded IA metadata jobs, item/file manifest expansion, review, and deeper extraction only through WorkUnits.

Why this block matters:
It avoids a future failure mode of building an abusive or brittle crawler.

Suggested future chapter/theme:
- Progressive Source Discovery

## Block 8 — TLS Verification Must Stay Enabled

Type:
- decision / risk control

Source status:
- FACT from IA-02 TLS tasks.

Text:
When the IA live probe failed due to local Python TLS trust, the chat chose diagnostics and local trust repair rather than disabling TLS verification. No unverified SSL context or insecure fallback was allowed.

Why this block matters:
It captures the project’s source-connector security posture.

Suggested future chapter/theme:
- Source Connector Safety

## Block 9 — PLAY as Product Legibility

Type:
- artifact / rationale

Source status:
- FACT from PLAY task statuses.

Text:
PLAY added a local demo corpus and smoke path: known hit, known absence, media SearchNeed, extraction/source SearchNeed, hard source-routing query, compatibility query, and blocked source/extraction/AI paths.

Why this block matters:
PLAY turns backend capability into something testable and explainable.

Suggested future chapter/theme:
- Making Local Systems Playable

## Block 10 — Repo Structure Is Governance, Not Cosmetics

Type:
- rationale

Source status:
- FACT from uploaded repo-structure canon and final repo discussion.

Text:
The repo should be structured by ownership roots, machine-readable contracts, and validators. It should not be reorganized by adding pretty folders or giant moves before current authority, generated state, and duplicate ownership are classified.

Why this block matters:
It explains how future repo cleanup should proceed.

Suggested future chapter/theme:
- Repository Structure as Architecture Governance

## Block 11 — SCOUT as Evidence Discovery, Not Popularity

Type:
- decision / rejection

Source status:
- INFERENCE / accepted design direction.

Text:
The Archillect-inspired SCOUT idea should become a relation graph over sources, tags, collections, aliases, files, and feedback, optimized for evidence and resolution value, not engagement or popularity.

Why this block matters:
It preserves the distinction between source-path learning and recommender-feed behavior.

Suggested future chapter/theme:
- Discovery Graphs and Source Trust

## Block 12 — Full IA Integration Remains Future Work

Type:
- unresolved issue / constraint

Source status:
- FACT as explicitly stated in chat.

Text:
The current system cannot yet browse Archive.org “in full,” crawl collections, fetch files, unpack archives, or index package members. That requires IA-HUNT bridge, scaled metadata expansion, file manifest processing, and later F0 extraction with safety gates.

Why this block matters:
It prevents overclaiming and guides next implementation phases.

Suggested future chapter/theme:
- From Metadata Pilot to Deep Connector
