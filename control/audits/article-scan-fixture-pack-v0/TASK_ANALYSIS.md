# Task Analysis

Target task: `article_inside_magazine_scan`.

Baseline after More Source Coverage Expansion v1:

- Archive eval counts: `capability_gap=1`, `satisfied=5`
- Remaining gap: `article_inside_magazine_scan`
- Reason: the bounded corpus had no article/page/OCR-like segment evidence
  inside a scanned magazine-like parent item.

Strict expected shape preserved:

- planner intent: `find_document_article`
- desired object: `document_article`
- minimum granularity: `article_or_page_range`
- required evidence: topic clue tied to scan/pages, page or article locator,
  and source-family visibility
- bad result avoidance: parent issue alone is insufficient, a collection title
  alone is insufficient, and modern unrelated ray-tracing material is not
  acceptable.

The task now uses source-backed fixture evidence for a synthetic article segment
with a parent issue, page range, OCR-like text fixture, and member path. It does
not use real OCR, PDF parsing, image parsing, or external source lookup.

