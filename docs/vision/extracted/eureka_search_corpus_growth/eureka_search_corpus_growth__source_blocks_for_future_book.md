# Source Blocks for Future Book — Eureka Search Engine: Corpus Growth, Public UX, and Resilient Search Planning

## Block 1 — Quality, tokens, and time

Type:
- goal / rationale

Source status:
- FACT

Text:
The user stated that the most important thing is not producing worse code than the best possible code, the next most important is not wasting tokens, and the next is not wasting time. Quality comes first, tokens second, time third.

Why this block matters:
This captures the project’s operating ethic. It explains why long-running test babysitting was rejected, but also why shortcuts that undermine correctness are unacceptable.

Suggested future chapter/theme:
Engineering discipline and AI-assisted development workflow.

## Block 2 — Stop launching from an empty shell

Type:
- decision / correction

Source status:
- FACT

Text:
The user rejected public alpha launch because the system did not yet work as a useful search engine: it did not search enough, had very few index entries, and manual index-building was not solving the core problem.

Why this block matters:
This was the turning point from launch-track work to active discovery and reviewed-corpus growth.

Suggested future chapter/theme:
Why Eureka deferred launch.

## Block 3 — Eureka as temporal object-resolution

Type:
- goal / rationale

Source status:
- FACT

Text:
The user recommended the north star: Eureka is a temporal object-resolution system that turns messy archive/source evidence into clear object states: verified artifact, reviewed metadata record, reviewed source lead, candidate, known need, or bounded absence.

Why this block matters:
This is the clearest product identity statement in the chat.

Suggested future chapter/theme:
Product identity and evidence model.

## Block 4 — Reviewed-corpus growth as the machine

Type:
- decision / next step

Source status:
- FACT

Text:
The user recommended that Eureka stop treating launch as the next milestone and make reviewed-corpus growth the machine. The repeated loop should be review, apply, project, and reassess.

Why this block matters:
This defines the operating cycle that should drive near-term work.

Suggested future chapter/theme:
The corpus-growth engine.

## Block 5 — Candidates are not truth

Type:
- rationale / constraint

Source status:
- FACT

Text:
Across the chat, candidates, live metadata observations, reviewed metadata records, source leads, reviewed needs, bounded absences, and verified artifacts are kept distinct. Metadata hits do not become verified artifacts, downloads, safety claims, rights claims, or public truth.

Why this block matters:
This is one of the strongest safety and epistemic constraints in the project.

Suggested future chapter/theme:
Object states and non-claim boundaries.

## Block 6 — Test discipline

Type:
- decision / rejection

Source status:
- FACT

Text:
The user rejected having AI sit in a loop while full unittest discovery ran. Long tests should run outside AI through local/CI harnesses, and AI should read compact summaries.

Why this block matters:
This informs future agent design and prevents expensive repetition.

Suggested future chapter/theme:
AI cost control and validation architecture.

## Block 7 — Public UX as search-first evidence surface

Type:
- design rationale

Source status:
- FACT

Text:
The public surface should be search-first, no-JS capable, evidence-first, and result-state explicit. Candidates must not look verified, and no-results should become a known-need/coverage/next-actions page.

Why this block matters:
This captures the public product design principle.

Suggested future chapter/theme:
Public search UX.

## Block 8 — Indexless fallback remains missing

Type:
- unresolved issue

Source status:
- FACT

Text:
The assistant answered that Eureka does not yet have a public website where anyone can search Archive.org and other remote sources live without indexes. The proposed missing capability is indexless live metadata fallback.

Why this block matters:
This prevents future readers from assuming live public search is already complete.

Suggested future chapter/theme:
Resilience and degraded-mode search.

## Block 9 — Launch gate remains strict

Type:
- decision / open condition

Source status:
- FACT

Text:
The launch gate repeatedly includes a larger reviewed corpus, at least several reviewed domains, reviewed artifact records, external full discovery, main promotion, publication rehearsal, and explicit manual approval.

Why this block matters:
This preserves the difference between internal demo readiness and public launch readiness.

Suggested future chapter/theme:
Launch readiness and governance.

## Block 10 — Latest completed state

Type:
- current state

Source status:
- FACT

Text:
The latest completed task visible before archiving is `SNAPSHOT-REFRESH-06`, with limited reviewed projections increased to 12 and candidate count after apply reported as 60. The next proposed task is `PUBLIC-ALPHA-REASSESS-06`, not yet completed.

Why this block matters:
This is the operational handoff state.

Suggested future chapter/theme:
Project status timeline.
