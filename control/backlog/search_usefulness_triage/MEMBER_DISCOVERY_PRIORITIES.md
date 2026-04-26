# Member Discovery Priorities

Member-level discovery is the secondary usefulness wedge. It is necessary when the requested object is inside a parent container.

Current support is bounded and fixture-driven. This triage does not claim broad member discovery is already implemented.

## Missing Pieces

1. member target refs
2. parent lineage
3. member path/hash/content type
4. member-level index records
5. source/evidence carried to member
6. bundle/member result cards
7. member action routing
8. parent container demotion when inner member exists

## Member Target Refs

Future member results need stable refs distinct from the parent:

```text
member:<parent-ref>#<member-path-or-id>
```

The exact contract is future work, but the next implementation should test that member identity is not collapsed into the parent container.

## Parent Lineage

Every member result should preserve:

- parent source id
- parent representation id
- parent artifact/container type
- member path
- evidence that the member was found inside the parent

## Member-Level Index Records

The local index should be able to record:

- member label/path
- content type
- textual snippet when available
- source family
- parent route hints
- member route hints

This must remain deterministic and not become ranking, fuzzy, vector, or semantic retrieval.

## Result Cards And Action Routing

Surfaces should eventually distinguish:

- parent bundle
- direct member
- unsupported member
- previewable text member
- fetchable local fixture member

Action routing should prefer the member when it is the smallest useful unit, while still showing the parent lineage.

## Parent Container Demotion

When the query asks for an INF, README, installer, article, or source file, a parent ISO/ZIP/magazine issue should not be presented as equally useful if member evidence exists.

## Tests To Add First

- member target-ref validation
- parent lineage preserved in member result
- member-level local index record generation
- member result card rendering
- hard eval query stays capability_gap unless direct member evidence exists

## Do Not Do

- do not add arbitrary local filesystem reads
- do not add broad extraction frameworks
- do not imply support for every archive format
- do not hide parent provenance
- do not weaken article-inside-scan expectations
