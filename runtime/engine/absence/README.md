# Runtime Engine Absence

This package holds Eureka's first bounded absence-reasoning seam.

It explains a miss in a compact, source-aware, evidence-aware way using only the
current bounded normalized catalog. It is intentionally narrow:

- no ranking
- no fuzzy retrieval
- no trust scores
- no merge logic
- no broad diagnostic engine

The current bootstrap lane supports:

- exact-resolution miss explanations
- deterministic search no-result explanations

The output is a compact absence report that records:

- what kind of request missed
- what bounded source families were checked
- a likely reason code and message
- a small bounded list of near matches when the current corpus supports them
- a short next-steps list

This is not the final absence, diagnostics, or reasoning architecture.
