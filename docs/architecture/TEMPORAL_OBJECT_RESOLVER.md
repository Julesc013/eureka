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

## Current Status

The current repo proves many bounded seams that support this direction:

- exact resolution
- deterministic search
- evidence summaries
- absence reasoning
- compatibility hints
- action routing
- decomposition and member readback
- multiple surfaces over one public boundary

What it does not yet prove is the full operational infrastructure for durable
investigation runs, source registries, indexing, memory, workers, or hosted
operation. Those belong to the next backend phase.
