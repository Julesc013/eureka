# Decisions, Open Questions, and Next Steps — Eureka HUNT, IA, SYN, and Artefact Resolution Planning

## Decisions

### Eureka should be a universal artefact-resolution engine

Status: final as product direction within this chat, though formal project adoption should still be reviewed.  
Who accepted it: The user repeatedly continued and expanded the framing; no rejection is visible.  
Rationale: The project’s use cases span software, drivers, hidden archive members, technical media, manuals, source packages, and provenance-obscured objects. A generic artefact-resolution kernel plus domain packs is more scalable than a narrow software finder.  
Consequences: Future tasks must build general resolution objects, domain packs, evidence pipelines, and action policies rather than one-off source scripts.  
Revisit conditions: Revisit only if the project deliberately narrows scope.

### HUNT is the active investigation spine

Status: final as architectural doctrine in this chat.  
Who accepted it: User proceeded through HUNT prompt generation and later reasoning built on it.  
Rationale: Search misses should create durable state, not dead ends.  
Consequences: SYN, IA, F, G, H, K, and future work must use Hunts, exhaustion reports, SearchNeeds, WorkUnits, review, and replay where applicable.  
Revisit conditions: Only if HUNT implementation proves unusable in actual local tests.

### IA metadata is the first real source-family proof

Status: final as near-term source strategy, with caveats around current repo verification.  
Who accepted it: User asked for a complete IA end-to-end connector and progressive IA search page.  
Rationale: IA has high-value metadata and a wide range of artefacts; it can be tested metadata-only without downloads.  
Consequences: IA should be developed as layered metadata/source-cache/evidence/review/index integration.  
Revisit conditions: If IA source policy, rate limits, or technical access make it unsuitable.

### Deep IA search must be progressive and budgeted

Status: final design direction in this chat.  
Who accepted it: User requested deep IA results; assistant reframed the design.  
Rationale: Searching the entire IA synchronously would be unsafe and impractical. Progressive lanes give interactivity without abuse.  
Consequences: UI/API should support result lanes, polling or streaming events, bounded source budgets, and deferred extraction.  
Revisit conditions: Revisit budget values after performance testing.

### SYN should be evaluation pressure, not fake evidence

Status: final principle in this chat.  
Who accepted it: Consistent with user’s anti-scaffold and evidence-first goals.  
Rationale: Synthetic data is useful for query and behavior testing, dangerous if mistaken for truth.  
Consequences: SYN can seed SearchNeeds and WorkUnits but cannot create verified records.  
Revisit conditions: Do not revisit the truth boundary; only adjust implementation details.

### Domain packs are the extensibility layer

Status: strong roadmap decision, not implemented in visible chat.  
Who accepted it: User asked to extend to every possible area; assistant proposed domain packs.  
Rationale: Domain packs prevent a generic kernel from becoming chaotic or hardcoded.  
Consequences: DOMAIN should be inserted after early SYN or before SYN integration.  
Revisit conditions: If a simpler schema can cover multiple domains without packs, but this seems unlikely.

### Public hosting and marketplace-style apps are later

Status: final prioritization for current phase.  
Who accepted it: No visible rejection; user’s focus remained local and IA.  
Rationale: Public production requires extensive operations, security, source policy, abuse controls, rights/takedown, and reliability work.  
Consequences: Continue local appliance and source/eval work before E/C/marketplace tracks.  
Revisit conditions: Only after E public alpha gates are designed and tested.

## Open Questions

### Is the IA/PLAY/HUNT work on `dev` now promoted to `main`?

Why it matters: SYN and future tasks should know whether to start from canonical `main` or active `dev`.  
Known: Visible chat reports `dev` ahead of `main` by 22 commits at one point.  
Unknown: Current repository state at archive time.  
Resolution path: Run GitHub/local branch comparison and promotion review.  
Priority: high.

### How much of IA deep search is already implemented?

Why it matters: The user wants a local HTML IA deep search page; we need to know whether IA-DEEP starts from planning or implementation.  
Known: Visible chat says IA metadata pilot reached reviewed local index proof.  
Unknown: Whether progressive UI lanes, event API, file manifest pages, and review-from-page flows exist.  
Resolution path: Inspect IA scripts, routes, runtime modules, workbench pages, and tests.  
Priority: high.

### Should IA-DEEP come before SYN-00?

Why it matters: IA-DEEP gives real source behavior for SYN to pressure-test; SYN gives evaluation pressure for IA.  
Known: The chat recommends interleaving: IA-08..IA-12, then SYN foundation, then IA closeout.  
Unknown: User’s operational priority after promotion.  
Resolution path: User decision after repo verification.  
Priority: medium-high.

### How soon should frontier-resolution media become a domain pack?

Why it matters: It is a strong second wedge and useful for SYN datasets.  
Known: User strongly identified it as a Eureka use case.  
Unknown: Whether to include it in DOMAIN-03 immediately or wait for more media observations.  
Resolution path: Add to DOMAIN plan or SYN seed family.  
Priority: medium.

### What is the minimum public alpha?

Why it matters: Production roadmap is long; a limited public alpha could be useful earlier.  
Known: Public production is not ready. Hosted local-index-only alpha was discussed as possible later.  
Unknown: Specific operational threshold for safe alpha.  
Resolution path: E-series planning after local/source/eval/ranking maturity.  
Priority: later.

## Next Steps

### 1. Verify repo state and decide promotion path

Priority: critical.  
Dependencies: local/GitHub branch state.  
Expected output: clear branch status and whether IA/HUNT/PLAY baseline is canonical.  
First action: compare `main` and `dev`.

### 2. If IA pilot is only on `dev`, run IA-to-main promotion review

Priority: high.  
Dependencies: IA pilot validation, AIDE checks, tests, no blockers.  
Expected output: either promote `dev` to `main` or record blockers.  
First action: generate or run IA-TO-MAIN-PROMOTION-REVIEW.

### 3. Plan IA-DEEP progressive connector

Priority: high if user wants IA search page next.  
Dependencies: IA pilot baseline.  
Expected output: IA-DEEP-00 plan with lanes, budgets, event model, policies, tests, and UI/API design.  
First action: produce IA-DEEP-00 prompt.

### 4. Start SYN over Local/HUNT/PLAY/IA

Priority: high after baseline is canonical or intentionally on dev.  
Dependencies: HUNT, PLAY, IA pilot.  
Expected output: synthetic/eval foundry plan and early taxonomy.  
First action: run SYN-00.

### 5. Add DOMAIN pack architecture

Priority: medium-high.  
Dependencies: early SYN taxonomy.  
Expected output: domain-pack architecture and initial packs.  
First action: DOMAIN-00.

### 6. Add SCOUT relation-guided discovery

Priority: medium.  
Dependencies: DOMAIN relations and HUNT/WorkUnit path.  
Expected output: candidate-only discovery trails and SourceTrust.  
First action: SCOUT-00.

### 7. Resume F0 extraction as hidden-member discovery

Priority: medium after SYN/DOMAIN/SCOUT.  
Dependencies: extraction policy, HUNT WorkUnits, domain/eval pressure.  
Expected output: safe member discovery from local fixtures through evidence/review/index.  
First action: F0-00.

## Rejected or Deferred Options

### Search all of Internet Archive synchronously

Why not carried forward: impractical, unsafe, likely abusive, and would block UI.  
Can return later: No as stated; only as progressive, budgeted deepening.

### Downloads and extraction during IA metadata search

Why not carried forward: rights, safety, malware, bandwidth, and product-truth risks.  
Can return later: Yes, through J action policies and F extraction gates.

### AI browsing as the main search mechanism

Why not carried forward: fragile, unsafe, candidate-only, and not evidence-grounded.  
Can return later: Yes, K or AI escalation gates.

### Public production before local/source/eval maturity

Why not carried forward: missing ops, abuse, security, privacy, backups, source policies.  
Can return later: Yes, through E hosting/public alpha and production gates.

### Treating generated AIDE state as truth

Why not carried forward: visible chat showed generated repo-health can be stale or contradictory.  
Can return later: No; generated state remains support metadata only.
