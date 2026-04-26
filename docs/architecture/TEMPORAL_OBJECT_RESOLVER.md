# Temporal Object Resolver

Eureka's target architecture is a temporal object resolver rather than a flat
archive-search stack.

The intended shape is:

```text
six logical graphs
+ five physical subsystems
+ one investigation planner
+ one action router
+ one resolution memory network
+ one eval-governed learning loop
```

## Resolver Framing

In a flat search system, work often looks like:

```text
query -> results
```

In Eureka's target model, work should look more like:

```text
query -> compiled task -> investigation run -> phased evidence -> actions or absence
```

That shift matters because users usually need more than text matching. They need
help identifying the right object, state, representation, action, and evidence
without manually reconstructing all of that from raw source results.

## Smallest Actionable Unit

The resolver should prefer the smallest useful unit that the user can act on:

- installer inside an ISO
- member inside a ZIP
- article inside a scan
- release asset inside a release page
- page range inside a larger document

This doctrine does not forbid showing the parent artifact. It requires the
parent to stop crowding out a stronger inner answer when the system has enough
evidence to expose that inner unit honestly.

Result Lanes + User-Cost Ranking v0 is the first bounded implementation of
that presentation rule. It assigns deterministic lane and user-cost hints to
current result records so inner members with lineage, evidence, and action
hints can be explained as lower effort than bulky parent bundles. It is not a
final production ranking engine.

## Current Status

The current repo proves many bounded seams that support this direction:

- exact resolution
- deterministic search
- evidence summaries
- absence reasoning
- compatibility hints
- action routing
- decomposition and member readback
- source registry, coverage-depth metadata, local indexing, and resolution runs
- synthetic member records for bounded local bundle fixtures
- deterministic result lanes and user-cost explanations for current results
- multiple surfaces over one public boundary

What it does not yet prove is broad live source coverage, final compatibility
evidence, production ranking, hosted operation, or native app delivery. Those
remain staged future work.
