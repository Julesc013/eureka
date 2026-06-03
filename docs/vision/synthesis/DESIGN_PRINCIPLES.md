# Design Principles

## Evidence-first resolution

Return object states with evidence and uncertainty. Do not present metadata, candidates, synthetic examples, or model outputs as truth.

## Fast learning, slow truth

Searches, misses, candidates, observations, and synthetic pressure can improve the system quickly. Only reviewed evidence-backed records become authoritative truth.

## Review before truth

Autonomy may discover. Candidates may propose. Evidence may support. Review may promote. This sentence is the strongest recurring governance principle in the corpus.

## Local-first product proof

A task is not complete merely because contracts, policies, examples, prompts, or validators exist. It should prove behavior through runtime code, persistent state where applicable, tests, audit evidence, and Workbench integration.

## One kernel, many projections

Workbench, public web, API, CLI/TUI, snapshots, relay, native, mobile, and agent contexts should project the same semantics. They must not fork product logic.

## Contracts own meaning

Semantic contracts, view model contracts, action contracts, representation profiles, and policy contracts should be the coordination layer. Direct page logic must not become source truth.

## Renderers are pure

Renderers should accept a view model, profile, skin, and policy context, then produce a representation. They must not query sources, mutate stores, promote candidates, infer facts, or decide policy.

## Explicit refusal and non-claims

The system should state what it cannot do: no live public fanout unless approved, no downloads unless gated, no extraction unless safe, no AI truth, no public production claim before operations are ready.

## Modularity through packs and adapters

Domain packs and source adapters should plug into stable kernels and contracts. Do not hardcode every source family or domain into the core.

## Source preservation and replayability

Observations, coverage, absence, WorkUnits, and review decisions should be preserved so hard searches do not disappear.

## Validation-first workflow

Use focused validators/tests in AI. Run broad/full discovery externally through a local/CI harness and feed compact summaries back into AI review.
