# Research Note: Temporal Object Resolution Engine

## Status

- Status: research note
- Scope: future-facing product and architecture direction beyond the current
  bootstrap slices
- Non-goal: this note does not by itself change accepted ADRs, public
  contracts, or current runtime claims

## Purpose

Capture a possible next operating layer for Eureka after the current bounded
bootstrap seams. The current repo already proves exact resolution,
deterministic search, evidence summaries, absence reasoning, compatibility,
action routing, decomposition, and member access. The next step should not be
"add a better search box." The candidate step is to treat search as a bounded
investigation that can stream, pause, resume, and reuse public evidence.

## Working Thesis

Eureka's long-term ceiling is not a search surface over source records. It is a
temporal object resolver that turns vague intent into the smallest usable
object or next action while keeping evidence, provenance, compatibility,
absence, and uncertainty visible.

In that framing:

- query input becomes a compiled resolution task, not just text
- search becomes a resolution run, not just a one-shot request
- reusable evidence matters more than repeated crawling
- absence findings are product value, not just failure states
- ranking should minimize user detective work, not only maximize text match

## Candidate Operating Layer

The candidate layer above the current bootstrap seams has five parts:

1. Investigation planner
   Compile raw input into a bounded task with object type, likely action,
   platform or time constraints, excluded interpretations, source lanes, and
   execution budget.

2. Resolution runs
   Represent long work as resumable, checkpointed, cancelable runs that can
   stream partial answers and remaining work.

3. Shared evidence network
   Reuse public extraction outputs, manifests, hashes, member listings,
   compatibility findings, and absence findings without treating private user
   history as shared product memory.

4. Resolution memory
   Preserve reusable strategy for query families: what worked, what was
   rejected, which sources helped, and what invalidates the memory later.

5. Eval-governed feedback loop
   Improve future slices against a hard benchmark of real archive-resolution
   tasks rather than intuition alone.

## Core Principles

### Return the smallest actionable unit

Prefer the member, installer, article, page, or direct representation that the
user can actually use. Do not make a parent bundle outrank a known useful inner
artifact just because its outer metadata matched first.

### Deterministic evidence outranks inference

Truth should continue to come from source records, hashes, identifiers,
manifests, timestamps, signatures, and extracted evidence.

Inference remains useful, but only as:

- candidate claim
- typed suggestion
- ranking feature
- explanation aid

It must not silently become canonical truth.

### Stream partial answers

Search quality should come from phased investigation:

- immediate local and cached evidence
- source metadata and exact matches
- graph or semantic expansion
- bundle and member inspection
- slower extraction or OCR
- final absence summary and next steps

### Share evidence, not personal behavior

Public shareable work should focus on:

- source metadata snapshots
- hashes and identifiers
- extraction manifests
- member listings
- public OCR or parsed text when allowed
- compatibility facts with evidence
- absence findings in reduced form

Private-by-default memory should include:

- local paths
- installed software
- opened files
- exact private history
- account-linked sources
- personal preferences

### Wrong-result suppression is first-class

The system should not only promote likely matches. It should also suppress known
bad interpretations such as OS images when the user likely wants compatible
applications or a direct inner artifact.

### AI is optional and bounded

The product should remain useful without LLMs. Deterministic evidence,
structured metadata, graph rules, lexical search, and lightweight ML come
first. If optional AI is introduced later, every output should remain typed,
evidence-linked, cacheable, and invalidatable.

## Candidate Ledger Model

If the direction above is adopted, the durable memory should likely be split
into distinct ledgers rather than one opaque "global memory":

- evidence ledger: source-backed claims, extracted facts, hashes, snippets
- identity ledger: same, variant, derivative, mirror, or successor claims
- resolution ledger: reusable solved-task patterns and negative constraints
- change ledger: invalidation events, refresh triggers, dependency edges

This split keeps source truth, artifact identity, search strategy, and freshness
separate enough to audit and evolve.

## Candidate Boundary Implications

This direction crosses multiple product boundaries, so those crossings should be
named early.

### `control/`

Owns research notes, benchmark definitions, source scorecards, and planning
material for future investigation or memory work.

### `contracts/`

Would eventually need governed types for things such as:

- resolution runs and streamed phases
- investigation status and remaining-work summaries
- evidence and absence summaries that can survive surface reuse
- public result lanes and action-oriented result envelopes
- shareable versus private memory policy boundaries

### `runtime/engine/`

Would own the planner, ranking features, invalidation behavior, identity logic,
resolution-memory use, and absence reasoning. It should still not depend on
surfaces, and it should still keep deterministic truth separate from inference.

### `runtime/connectors/`

Would continue to emit source records, extraction outputs, and evidence through
engine interfaces only. Connectors still must not invent object truth or own
trust semantics.

### `runtime/gateway/`

Would become the broker for transport-neutral investigation status, streamed
result lanes, and public action routing built over engine interfaces and
contracts.

### `surfaces/`

Would present guided investigation UX: best current answer, remaining work,
bounded evidence, compatibility hints, and explicit next actions.

## Candidate Next Bounded Slices

If Eureka chooses to test this direction, the next bounded slices should remain
small and honest:

1. Add a governed eval corpus for hard archive-resolution tasks under `evals/`
   before expanding ranking or retrieval claims.
2. Introduce a transport-neutral `resolution_run` or investigation-status seam
   without changing the current exact-resolution path.
3. Add a bounded result-lane view model so surfaces can distinguish direct
   answers, bundle-contained answers, official sources, and absence-oriented
   traces.
4. Add a content-addressed evidence or extraction record seam for reusable
   member listings and parsed manifests without introducing a final shared cache
   service.
5. Define an explicit private-versus-shareable memory policy before any durable
   resolution-memory implementation is attempted.

## Explicit Non-Decisions

This note does not settle:

- the final global object identity model
- a final claim ontology or trust model
- a production queue or workflow stack
- whether future memory is local-only, hosted, or federated
- whether any graph store is required
- whether any vector index is required
- whether AI is needed for any specific slice
- final public API shapes for streaming, search, or actions

## Questions To Carry Forward

The following questions should remain open until bounded slices exist:

1. Which parts of a compiled investigation plan belong in governed contracts
   versus engine-private planning?
2. What is the first durable unit of shareable public evidence: source record,
   extraction manifest, member listing, or absence finding?
3. How should Eureka express invalidation dependencies without overcommitting to
   one storage model?
4. Which ranking dimensions deserve first-class contracts, and which should
   remain runtime policy features?
5. When a result is "best for action" but not "best for provenance," how should
   the product explain that tradeoff honestly?
6. Which search tasks should remain deterministic forever, and which justify
   optional ML or LLM assistance later?
