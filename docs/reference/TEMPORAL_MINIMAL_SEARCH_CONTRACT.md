# Temporal Minimal Search Contract

`contracts/surface/ui/temporal_minimal_search.v0.json` defines Eureka's search-like
presentation language for public surfaces.

Temporal Minimal Search is not a separate site and not a clone of any search
engine. It allows neutral classic search grammar: sparse pages, blue links,
source/status lines, compact metadata, obvious GET forms, and text-first
fallbacks. It forbids copied logos, exact external search-engine page identity, exact
external search-engine CSS/HTML, affiliation claims, deceptive source labels, and
misleading official labels.

## Doctrine

- Sparse, fast, text-first, and link-first.
- No-JS baseline with normal links and GET forms.
- Old clients lose polish before meaning.
- Standard, lite, text, file-tree, print, high-contrast, future terminal, and
  future native-card projections are profiles over the same semantics.

## Semantic Visibility

Visual simplification must keep visible:

- object, source, result, need, candidate, and evidence identity
- source and evidence posture
- candidate/provisional/review state
- compatibility caveats
- rights and risk posture
- limitations, unresolved gaps, absence scope, and blocked actions
- public/static/hosted limitations

## Validation

```text
python scripts/validate_temporal_minimal_search.py
```

The validator checks doctrine, visual principles, accessibility and old-client
principles, forbidden branding/trade-dress rules, product-claim boundaries, the
design profile matrix, representation profile references, and examples.
