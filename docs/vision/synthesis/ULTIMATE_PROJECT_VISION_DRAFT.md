# Ultimate Project Vision Draft

## 1. What the project is

Eureka wants to become a temporal artefact-resolution system: a way to turn messy archive/source evidence into explicit object states. The public face may look like search, but the stable core is not a search box. It is a governed resolver that can say: this object is verified, this one is a candidate, this one is a near miss, this one is a known need, this one is blocked by policy, this one is only metadata, and this one is absent within a stated coverage boundary.

The project’s recurring center is evidence. Eureka should preserve where a claim came from, what it supports, what it does not support, who or what reviewed it, which actions are allowed, and what remains unresolved. This makes it different from a crawler, downloader, app store, emulation front-end, public search fanout, AI answer engine, or generic archive wrapper.

## 2. Stable core idea

The stable core can be summarized as:

```text
query
→ reviewed local knowledge if available
→ unresolved state if not
→ governed Hunt / ResolutionRun
→ SearchNeeds and WorkUnits
→ source observations
→ evidence candidates
→ review
→ reviewed local index
→ better future search
```

The corpus repeatedly states the same trust boundary in different words: autonomy may discover; candidates may propose; evidence may support; review may promote; only reviewed evidence-backed records become public truth. The related maxim is “fast learning, slow truth”: every search can improve the system, but only reviewed evidence should enter authoritative indexes.

## 3. Product layers

Eureka has several layers that should not be confused.

The **domain core** owns object identity, source observations, evidence, candidates, needs, reviews, actions, policy state, and result meaning.

The **ResolutionRunKernel** should own query/run behavior: run creation, commands, events, WorkUnits, lanes, coverage reports, policy gates, blocked-action posture, and projection-safe output.

The **SurfaceKernel / TSIS layer** should own route resolution, canonical view-model loading, capability negotiation, representation selection, renderer dispatch, cache keys, output policy, fallback rules, and semantic parity across clients.

The **Workbench** should be the internal/operator superset of the product: the richest cockpit for Hunts, WorkUnits, source observations, candidates, evidence, review, index rebuilds, SYN, DOMAIN, SCOUT, extraction, snapshots, relay, and operations.

The **public product** should be a constrained projection of the same packets and view models. It should not fork truth, source logic, review logic, policy logic, or object identity.

The **future ecosystem** can include CLI/TUI, API, snapshot/relay, native, mobile, old-browser, terminal, and agent-facing surfaces. They should consume negotiated representations, not duplicate the product.

## 4. Current truth versus advisory ambition

The archive says the project has passed through Local Appliance, HUNT, PLAY, and an IA metadata pilot, with reports of source-cache, evidence-candidate, provisional-candidate, review/promotion dry-run, reviewed-index, and search/object/absence proof. These are important historical claims, but this corpus did not include the live repo. They remain archive-historical and conversation-advisory until verified against current repo authority.

The corpus is clear about non-claims. Eureka is not production-ready. It is not a public Archive.org crawler. It does not yet prove full Archive.org integration, downloads, file fetching, hidden-member extraction, Wayback replay, arbitrary live source fanout, marketplace behavior, accounts, telemetry, or AI-made truth.

## 5. Design doctrine

The strongest future doctrine is the Temporal Semantic Interface System. Eureka should have one semantic product language: one object model, one route model, one evidence model, one action model, one resolution/run model, one capability model, many representations, many skins, many clients, and no duplicated product logic.

This means Eureka does not really have “pages” as truth. It has semantic entities and view-model contracts that can render as JSON, text, terminal, HTML2/HTML3.2/classic, rich web, native cards, snapshots, file manifests, or future agent context. A renderer must not query sources, mutate indexes, promote candidates, decide policy, or invent facts. It should only project an authorized view model through a profile and skin.

## 6. Rejected directions

The corpus consistently rejects several tempting moves:

- launching public alpha from a thin or empty corpus;
- letting public search fan out live to arbitrary sources;
- synchronously searching all of Archive.org while a user waits;
- treating IA metadata as verified truth;
- doing downloads, installs, package manager execution, emulators, VMs, or hidden extraction before policy and safety gates;
- treating synthetic data as evidence;
- using AI/model output as truth, rights clearance, malware safety, or index mutation;
- adding all source families before a reusable run/workbench/source architecture exists;
- creating separate product logic for rich web, classic web, terminal, native, API, snapshot, and agent surfaces;
- mistaking AIDE/generated state for product truth;
- treating old prompt IDs, audit names, and scaffolding vocabulary as runtime architecture.

## 7. Long-horizon ambition

The long horizon is broader than old software search. Eureka could become a cross-domain resolver for hidden archive members, drivers, manuals, packages, source releases, metadata-only traces, compatibility records, provenance-obscured media, advanced-format cultural/technical artifacts, and future domain packs. Domain packs should define object types, identifier patterns, source families, metadata fields, risk/rights rules, action policies, query examples, eval sets, and renderer hints.

SCOUT can later add relation-guided discovery across collections, uploaders, tags, filename patterns, platform families, member paths, and source trails. F extraction can later turn nested containers, ZIP/ISO/WARC/WACZ/package/source/PDF/OCR layers into safe hidden-member discovery. Snapshots and relay can make the system consumable offline and across decades of clients.

## 8. Practical near-term vision

The “this is real” milestone should be concrete:

```text
type a query in a local Workbench page
→ see reviewed local hits immediately
→ create or inspect a ResolutionRun/Hunt
→ start a bounded IA metadata WorkUnit
→ watch lanes/events/candidates/evidence appear
→ review one candidate
→ preview promotion
→ rebuild the reviewed local index
→ rerun the query and see a reviewed IA-backed result
```

That milestone is more valuable than more prompt expansion or a premature public launch. It proves the resolver loop, the evidence boundary, the Workbench role, the source connector pattern, and the future public projection model.

## 9. What should happen after this corpus

For the archive process, the next output should be the readable book, built from this corpus and synthesis rather than from evidence-card machinery.

For implementation planning, the next move should be current-state verification and closeout, followed by TSIS doctrine/contracts and then run/workbench/source integration. No archive claim should become canon until verified against the repo’s authority order.
