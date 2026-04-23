# Bounded Acquisition

`runtime/engine/acquisition/` holds the first bounded acquisition and fetch seam
for Eureka.

This slice proves that Eureka can:

- take one already resolved target
- accept one explicit bounded `representation_id`
- retrieve a tiny deterministic fixture-backed payload for fetchable
  representations
- return a structured unavailable or blocked result for non-fetchable or
  unknown representations

This slice does **not** introduce:

- live downloads
- installers or launchers
- import or restore flows
- background orchestration
- final download semantics

The service only follows bounded local fixture locators already carried through
normalized representation summaries.
