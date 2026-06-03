# Source Blocks for Future Book — Eureka HUNT, IA, SYN, and Artefact Resolution Planning

## Block 1 — From Search Engine to Artefact Resolution Engine

Type:
- explanation / decision

Source status:
- INFERENCE, based on repeated visible discussion

Text:
Eureka should not be understood as a simple search engine for old software. The stronger framing is a universal artefact-resolution engine: given an incomplete or ambiguous query, it resolves the likely object, finds or investigates the smallest actionable artefact, explains evidence and uncertainty, and turns unresolved gaps into future work.

Why this block matters:
This is the central conceptual expansion of the project. It can anchor a future chapter on Eureka’s identity.

Suggested future chapter/theme:
Product identity; artefact-resolution model.

## Block 2 — Search as a Resumable Investigation

Type:
- explanation / rationale

Source status:
- FACT, explicitly stated in chat in multiple places

Text:
A search is not just a lookup. It is a resumable, steerable, evidence-producing investigation. If Eureka already knows the answer, it should return it. If not, it should start a governed Hunt, create SearchNeeds and WorkUnits, expose what was checked, and preserve the unresolved state for future work.

Why this block matters:
This is the basis for HUNT and differentiates Eureka from ordinary search.

Suggested future chapter/theme:
Search Hunt Sessions; investigation spine.

## Block 3 — Synthetic Queries Create Pressure, Not Truth

Type:
- rationale / constraint

Source status:
- FACT, explicitly stated in chat

Text:
Synthetic queries may generate demand, tests, expected behavior, SearchNeed seeds, and WorkUnit seeds. They must not generate authoritative evidence, verified object records, safety claims, rights claims, hashes, or master-index records. Synthetic queries create pressure. Real sources create evidence. Review creates truth.

Why this block matters:
This defines SYN’s safety boundary.

Suggested future chapter/theme:
Synthetic Query Foundry; evaluation without fabrication.

## Block 4 — The IA Progressive Lane Model

Type:
- next step / design

Source status:
- FACT as a proposed design in visible chat

Text:
The desired IA search page should return reviewed local results immediately, then show local candidates and source-cache hits, then bounded live IA metadata candidates, then item metadata and file manifests, then evidence candidates and review state, and finally reviewed-index updates. Deep extraction remains deferred to F0.

Why this block matters:
This is the clearest user-facing IA product design in the chat.

Suggested future chapter/theme:
Internet Archive connector; progressive results.

## Block 5 — The Local Workbench as Product Proof

Type:
- rationale

Source status:
- FACT, repeated in chat

Text:
Future work should be grounded in a real local hosted system: local server, HTML page, reviewed public index, WorkUnit queue, source probe runner boundaries, review flow, index rebuild, and smoke tests. Contracts, policies, examples, and validators alone are not completion.

Why this block matters:
This captures the move away from scaffold-only development.

Suggested future chapter/theme:
Local Appliance; product proof.

## Block 6 — Review as the Truth Boundary

Type:
- decision / constraint

Source status:
- FACT, repeatedly stated

Text:
Autonomy may discover. Candidates may propose. Evidence may support. Review may promote. Only reviewed evidence-backed records become public truth.

Why this block matters:
This is the trust model of the entire system.

Suggested future chapter/theme:
Evidence ledger and review queue.

## Block 7 — Frontier-Resolution Media as a Second Wedge

Type:
- goal / domain expansion

Source status:
- FACT, based on user-provided passage and assistant response

Text:
The user identified advanced-format everyday-life documentation, such as the 1993 New York D-Theater/D-VHS clip, as exactly the sort of hard artefact Eureka should find. This broadened Eureka from old software and drivers into provenance-obscured media, format lineage, representation quality, and cultural/technical artefact resolution.

Why this block matters:
This shows how Eureka becomes cross-domain.

Suggested future chapter/theme:
Domain packs; frontier-resolution media.

## Block 8 — Prompt Vocabulary Must Not Become Runtime Architecture

Type:
- risk / rejection

Source status:
- FACT, visible in earlier transcript summaries

Text:
The chat repeatedly warned that H-series task IDs, bundle labels, fixture-only naming, and audit vocabulary should not leak into production runtime architecture. Task IDs belong in control/audit layers, not in runtime service names, public schema IDs, or domain models.

Why this block matters:
This explains why R0 recovery and leakage remediation mattered.

Suggested future chapter/theme:
Architecture hygiene; anti-scaffold doctrine.

## Block 9 — Main/Dev Reconciliation as Product Quality

Type:
- decision / rationale

Source status:
- FACT as discussed in visible branch sync sections; exact branch state may be stale

Text:
When `main` and `dev` diverged, the chat treated branch reconciliation as a product task. The goal was to bring the newer AIDE/source-slice baseline from `main` into `dev` while preserving HUNT/search work, not to replace one branch with the other.

Why this block matters:
This demonstrates governance maturity.

Suggested future chapter/theme:
AIDE control plane and branch discipline.

## Block 10 — IA Is the First Real Source Family, Not Full IA Integration

Type:
- decision / constraint

Source status:
- FACT as a visible recommendation

Text:
Internet Archive should be the first source-family proof, but the initial target is metadata-only local pilot and progressive metadata/file-manifest search, not full archive.org integration, downloads, collection crawling, or Wayback replay.

Why this block matters:
This prevents unsafe scope explosion.

Suggested future chapter/theme:
Source connector pattern; IA pilot.

## Block 11 — Domain Packs as the Modularity Layer

Type:
- design

Source status:
- FACT as a proposed roadmap decision

Text:
To support every possible area, Eureka should not hardcode domain logic into the kernel. It should use domain packs that define object types, source families, identifier patterns, metadata fields, compatibility or format rules, risk/rights rules, action policies, query examples, eval sets, and renderer hints.

Why this block matters:
This is the path to generality.

Suggested future chapter/theme:
Domain pack architecture.

## Block 12 — SCOUT as Relation-Guided Discovery

Type:
- future work

Source status:
- FACT as a proposed roadmap element

Text:
SCOUT should learn relation paths such as same collection, same uploader, same format family, same filename pattern, same platform, same catalogue, same package family, and same member path pattern. It emits candidates, discovery trails, trust observations, and WorkUnits, not accepted truth.

Why this block matters:
This shows how Eureka becomes more intelligent without immediately relying on AI.

Suggested future chapter/theme:
Curator Graph and discovery intelligence.

## Block 13 — F Is Hidden-Object Discovery, Not Archive Tooling

Type:
- rationale / future work

Source status:
- FACT as a proposed roadmap element

Text:
F extraction should not be a generic archive tool. It should be HUNT/SYN/DOMAIN/SCOUT-driven hidden-object discovery: query → Hunt → extraction SearchNeed → extraction WorkUnit → safe container fixture → member observations → evidence candidates → review → reviewed index → search hit.

Why this block matters:
This preserves safety and product integration for extraction.

Suggested future chapter/theme:
Deep extraction/member discovery.

## Block 14 — Public Production Is Still Far

Type:
- status / risk

Source status:
- FACT as repeatedly stated in visible chat; exact readiness estimates are assistant estimates

Text:
The chat repeatedly stated that Eureka is not production-ready or public-launch-ready. Public stable hosting still requires operations, security, abuse controls, rate limits, privacy, backups, rollback, observability, takedown workflow, source policy enforcement, API stability, and a larger reviewed corpus.

Why this block matters:
Prevents premature public claims.

Suggested future chapter/theme:
Production readiness and public alpha gates.

## Block 15 — The Desired IA User Experience

Type:
- user goal / next step

Source status:
- FACT, based on the user’s final substantive request

Text:
The user wants to spin up a local HTML page, enter a query, have Eureka search the Internet Archive deeply, and see potential results come through progressively while the index is searched first and deeper IA metadata, files, archives, subdirectories, and packaged files are discovered later.

Why this block matters:
This is the clearest near-term product experience target.

Suggested future chapter/theme:
Progressive IA search UI.

## Block 16 — No Dead Ends

Type:
- rationale

Source status:
- INFERENCE from repeated HUNT/SYN/WorkUnit discussion

Text:
The most valuable improvement is that no hard search should disappear. A failed or weak search becomes structured reusable state: Hunt, SearchNeed, WorkUnits, evidence candidates, and future eval pressure.

Why this block matters:
This is the compounding mechanism.

Suggested future chapter/theme:
Learning loop and durable unresolved needs.
