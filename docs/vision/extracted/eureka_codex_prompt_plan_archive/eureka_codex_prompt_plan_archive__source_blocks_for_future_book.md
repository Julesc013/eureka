# Source Blocks for Future Book — Eureka Codex Prompt Plan and Production Roadmap

Date anchor: 2026-05-31 Australia/Melbourne

## Block 1 — Blockers Must Be Resolved Autonomously

Type:
- decision / rationale

Source status:
- FACT

Text:
The user corrected the prompt strategy by saying that blockers should catch mistakes and errors, but the agent should not stop or ask for input when blockers appear. The prompts should assume Codex is a clean-room developer and include enough context for it to resolve blockers autonomously.

Why this block matters:
This captures a major operational design principle for the Codex queue: prompts must be self-contained, rationale-rich, and safe enough for autonomous blocker resolution.

Suggested future chapter/theme:
Autonomous Development Workflow and Clean-Room Prompt Design

## Block 2 — P50 as the Factual Checkpoint

Type:
- artifact / decision

Source status:
- FACT

Text:
The user reported that P50 was complete and pushed, with commits adding a full Post-P49 audit pack, a stdlib-only validator, focused tests, metadata wiring, and no product behavior such as live probes, hosted backend, source calls, pack import, AI runtime, index mutation, or deployment changes.

Why this block matters:
P50 is the visible point where the project shifted from accumulated contracts/plans into an explicit factual audit baseline.

Suggested future chapter/theme:
The Post-P49 Audit and Project Discipline

## Block 3 — Eureka as Evidence-First Resolver

Type:
- explanation / goal

Source status:
- FACT

Text:
The visible synthesis described Eureka as an evidence-first temporal object resolver, not merely a better archive.org search, Google clone, scraper, app store, downloader, or LLM wrapper.

Why this block matters:
This is the core product identity. It should anchor any future book chapter about what Eureka is.

Suggested future chapter/theme:
Product Thesis: Evidence-First Temporal Object Resolution

## Block 4 — Fast Learning, Slow Truth

Type:
- rationale

Source status:
- FACT

Text:
The repeated controlling doctrine was that public searches may improve the shared system, but only validated, evidence-backed records should enter authoritative indexes. This was summarized as “Fast learning, slow truth.”

Why this block matters:
This phrase condenses the system’s governance model and should be preserved.

Suggested future chapter/theme:
Governance and Truth Boundaries

## Block 5 — Public Search Must Not Fan Out Live

Type:
- decision / risk

Source status:
- FACT

Text:
Across the generated prompts, public search was repeatedly prohibited from live fanout to Internet Archive, Wayback, GitHub, PyPI, npm, Software Heritage, arbitrary URLs, or connector runtimes. It should remain controlled and local-index-only until later approval.

Why this block matters:
This is one of the most important safety boundaries in the project.

Suggested future chapter/theme:
Public Search Safety and Source Boundaries

## Block 6 — Generated Through P107, Live Around P95

Type:
- unresolved issue / status

Source status:
- FACT for user statement; UNVERIFIED for repository state

Text:
The user stated that prompts had been generated up to P107, while the live repository was still around P95. The assistant treated this as the working fact but did not independently verify it.

Why this block matters:
This is the key state caveat for future continuation.

Suggested future chapter/theme:
Execution Lag and Prompt Queue Management

## Block 7 — Do Not Keep Expanding Forever

Type:
- next step / rationale

Source status:
- INFERENCE / assistant recommendation

Text:
The assistant recommended that the project should execute P96–P107, then run a consolidation audit before generating an unlimited new prompt sequence.

Why this block matters:
It identifies the transition from architecture expansion to execution discipline.

Suggested future chapter/theme:
From Roadmap to Implementation

## Block 8 — Manual Observation Batch 0 Is Human Work

Type:
- decision / unresolved issue

Source status:
- FACT

Text:
The prompt sequence treated Manual Observation Batch 0 as human-operated work. Codex must not perform external observations, browse external sites, or fabricate external results.

Why this block matters:
It preserves the evidence boundary for external baseline comparisons.

Suggested future chapter/theme:
External Baselines and Human Evidence

## Block 9 — Connectors Need Approval Before Runtime

Type:
- rationale / decision

Source status:
- FACT

Text:
The first-wave connectors—Internet Archive, Wayback/CDX/Memento, GitHub Releases, PyPI, npm, and Software Heritage—were split into approval packs, runtime planning, audits, and only later possible live probes.

Why this block matters:
It explains why live connector implementation was deferred despite being central to the product.

Suggested future chapter/theme:
Source Connectors and Approval Gates

## Block 10 — Dry-Runs Are Not Authoritative Stores

Type:
- rationale / risk

Source status:
- FACT

Text:
Source cache, evidence ledger, page, pack import, and ranking dry-runs were designed to prove loading, classification, validation, rendering, and reporting without becoming authoritative runtime or mutating indexes.

Why this block matters:
This prevents future readers from confusing local dry-run code with production functionality.

Suggested future chapter/theme:
Dry-Run Before Runtime

## Block 11 — The Resolver Product Layer

Type:
- explanation

Source status:
- FACT

Text:
Object pages, source pages, comparison pages, identity resolution, merge/deduplication, ranking, and explanations were designed as the layer that turns search results into a resolver product.

Why this block matters:
It identifies the major user-facing product shift in the roadmap.

Suggested future chapter/theme:
From Results to Resolution

## Block 12 — Deep Extraction Handles the Hidden Object Problem

Type:
- explanation / goal

Source status:
- FACT

Text:
The deep extraction contract was motivated by the observation that the wanted object is often inside a ZIP, ISO, installer, WARC, WACZ, package archive, source repository snapshot, scanned volume, PDF, OCR layer, metadata manifest, or nested member.

Why this block matters:
This explains why extraction is central to archive discovery, not an optional feature.

Suggested future chapter/theme:
Finding Things Inside Containers

## Block 13 — Public Alpha Should Be Minimal and Honest

Type:
- next step / rationale

Source status:
- INFERENCE / assistant recommendation

Text:
The assistant recommended a first live alpha consisting of a static site plus hosted backend querying a controlled local/public index, with no live fanout, uploads, downloads, accounts, telemetry, or production overclaims.

Why this block matters:
This is the practical launch strategy emerging from the chat.

Suggested future chapter/theme:
The First Public Alpha

## Block 14 — AI Is Deferred and Bounded

Type:
- rejection / boundary

Source status:
- FACT

Text:
AI/model runtime was repeatedly kept out of near-term implementation. AI outputs, if ever used, should be typed candidates and never truth, rights clearance, malware safety, source trust, ranking acceptance, or master-index mutation.

Why this block matters:
It prevents Eureka from being reframed as an LLM-first search wrapper.

Suggested future chapter/theme:
AI as Bounded Research Assistance

## Block 15 — The Larger Roadmap

Type:
- next step / artifact

Source status:
- INFERENCE / assistant plan based on chat

Text:
The final broad plan moved from executing P96–P107 into P108–P115, public alpha hardening, manual baselines, authoritative local source/evidence stores, first approved connector path, pages, explanations, ranking, pack import, deep extraction, more connectors, and app-store-style clients.

Why this block matters:
This is the clearest visible roadmap from the current prompt queue to the larger product.

Suggested future chapter/theme:
Roadmap from Prototype to Ecosystem
