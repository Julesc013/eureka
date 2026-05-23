# Design Tokens Contract

`contracts/surface/ui/design_tokens.v0.json` defines Eureka's generic design-token
shape for future renderers.

Design tokens are contracts, not output. They may guide future HTML, lite HTML,
HTML 3.2-ish, text, file-tree, JSON, snapshot, relay, terminal, native-card,
print, and high-contrast renderers, but they must not change route identity,
source posture, evidence posture, candidate/review state, rights, risk,
limitations, blocked actions, or product-boundary meaning.

## Required Families

Every token set must carry compact families for color, typography, spacing,
density, borders, layout, links, forms, tables, badges, warnings, actions,
compatibility, rights/risk, evidence/source, accessibility, and degradation.

The contract intentionally stays small. It is not a component library, CSS
framework, or renderer implementation.

## Product Boundary

Token sets must keep product-boundary booleans false. A token set cannot claim
hosted behavior, live probes, source sync, source connectors, downloads,
uploads, accounts, telemetry, rights clearance, malware safety, exhaustive
global search, automatic promotion, or search-engine affiliation.

## Validation

```text
python scripts/validate_design_tokens.py
```

This validator checks the schema, policy inventory, concrete token inventory,
and token examples with only the Python standard library.
