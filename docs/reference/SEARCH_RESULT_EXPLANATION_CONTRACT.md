# Search Result Explanation Contract v0

Status: contract-only.

Search Result Explanation Contract v0 defines the future public-safe shape for explaining why a result appeared, what matched, what evidence supports it, what source and compatibility limits apply, what ranking/grouping/identity reasoning may be referenced, what is missing, and what safe actions remain available.

P96 does not implement runtime explanation generation. It does not change public search responses, public search ordering, result suppression, hidden scores, ranking, model calls, telemetry, source cache, evidence ledger, candidate index, public index, local index, runtime index, or master index. It has no suppression path.

## Contract Files

- `contracts/search/search_result_explanation.v0.json`
- `contracts/search/search_result_explanation_component.v0.json`
- `contracts/search/search_result_explanation_policy.v0.json`
- `control/inventory/search/search_result_explanation_policy.json`
- Examples under `examples/search_result_explanations/`

## Required Model

Each explanation has:

- an explanation scope and explained result
- query interpretation without raw private query text
- match and recall explanation with checked and not-checked scope
- source coverage explanation
- evidence and provenance explanation
- identity, grouping, and deduplication explanation
- ranking relationship without hidden numeric scores
- compatibility caveats
- absence, near-miss, and gap explanations
- action safety and rights/risk cautions
- user-facing summary and audit-readable components
- API and static/lite/text future projections
- privacy, no-truth, no-runtime, and no-mutation guarantees

## Component Taxonomy

Components include query interpretation, lexical match, phrase match, identifier match, alias match, source match, metadata field match, compatibility match, representation match, member match, evidence strength, provenance strength, source coverage, ranking reason, grouping reason, identity reason, conflict warning, candidate warning, absence explanation, near-miss explanation, gap explanation, action safety, rights/risk caution, privacy redaction notice, not-checked notice, and unknown.

## Copy Policy

User-facing copy must use plain language, avoid false certainty, avoid marketing claims, avoid unscoped "best" language, mention unchecked live sources, mention provisional or candidate status, and show conflicts and gaps. It must not claim rights clearance, malware safety, dependency safety, installability, global absence, or accepted truth without review.

## Relationships

Public search result cards may later carry an explanation ref or inline summary only after a future runtime gate. Object, source, and comparison pages may cite explanation components after their own runtime gates. Identity, merge, evidence-weighted ranking, compatibility-aware ranking, source cache, evidence ledger, candidate index, known absence, and deep extraction contracts are inputs for future explanation references, not runtime behavior in P96.

## Runtime Boundary

No runtime route, public search response mutation, public search order change, ranking execution, model call, telemetry, source/evidence/candidate/public/local/master mutation, download, install, or execution is added.
