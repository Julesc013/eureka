# Security And Abuse Review

Required future controls:

- explanation length cap
- component count cap
- no raw private query
- no path, URL, source, explanation, ranking, cache, ledger, candidate, model, or
  filesystem selector parameters
- no local file access
- no live source calls
- no model calls
- no hidden scores
- no result suppression
- no telemetry
- prompt-injection-like text treated as data, not instruction
- source/evidence labels escaped
- HTML rendering escapes content
- public user text bounded
- operator kill switch

Abuse risks include explanation endpoint scraping, component amplification, URL
smuggling through labels, private data leakage, hidden score inference, and
marketing-style overclaims. These risks block hosted mode until operator review.

