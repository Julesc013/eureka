# Member Discovery Priorities

Member-level discovery is the secondary usefulness wedge. It is necessary when the requested object is inside a parent container.

Current support is bounded and fixture-driven. Member-Level Synthetic Records
v0 now implements the first deterministic member-record seam for committed
local bundle fixtures. This still does not claim broad member discovery across
all source families or archive formats.

## Missing Pieces

1. broader member target refs beyond committed local bundle fixtures
2. richer result cards beyond the current v0 lane/user-cost summaries
3. member action routing beyond explicit existing read/preview hints
4. parent container demotion when inner member exists
5. member-level records for Internet Archive file lists, scanned/OCR content,
   WARC/WACZ, source archives, and future fixture families

## Member Target Refs

Current bounded member results use stable refs distinct from the parent:

```text
member:sha256:<sha256(parent-target-ref + normalized-member-path)>
```

The digest-based target ref intentionally avoids private paths while preserving
the reversible parent/member path metadata in the record body. Future contract
work should decide which parts become durable public compatibility promises.

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

Member-Level Synthetic Records v0 now indexes `synthetic_member` records for
the committed local bundle fixture members. Result Lanes + User-Cost Ranking v0
now gives those records lower deterministic user cost than parent bundles when
member path, parent lineage, evidence, and action hints are present. This is a
bounded explanation seam, not final relevance ranking.

## Result Cards And Action Routing

Surfaces should eventually distinguish:

- parent bundle
- direct member
- unsupported member
- previewable text member
- fetchable local fixture member

Action routing should prefer the member when it is the smallest useful unit, while still showing the parent lineage.

Current v0 projection shows lane and user-cost hints in search, local-index,
exact-resolution, CLI, web, and HTTP API output. Future result-card work should
make those hints easier to scan without hiding the parent bundle.

## Parent Container Demotion

When the query asks for an INF, README, installer, article, or source file, a parent ISO/ZIP/magazine issue should not be presented as equally useful if member evidence exists.

## Tests To Add First

- result-lane member-vs-parent promotion tests
- member result card rendering
- compatibility evidence carried to member tests
- hard eval query stays capability_gap unless direct member evidence exists

## Do Not Do

- do not add arbitrary local filesystem reads
- do not add broad extraction frameworks
- do not imply support for every archive format
- do not hide parent provenance
- do not weaken article-inside-scan expectations
