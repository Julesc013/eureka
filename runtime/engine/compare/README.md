# Engine Compare

`runtime/engine/compare/` holds the first bounded comparison and disagreement seam for Eureka.

Current bootstrap scope:

- compare exactly two bounded target refs side by side
- resolve each side through the existing exact-resolution path
- preserve bounded evidence summaries per side
- surface compact agreements and disagreements explicitly
- no merge engine
- no trust ranking
- no final truth-selection model

This slice is intentionally small and replaceable. It proves that Eureka can keep
multiple source-backed claims visible side by side without silently collapsing them.
