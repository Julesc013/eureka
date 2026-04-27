# Changes Made

- Added `article-scan-recorded-fixtures` to the governed source inventory.
- Added `runtime/connectors/article_scan_recorded/` as a stdlib-only recorded
  fixture connector.
- Added ingest, extract, and normalize boundary types for article-scan recorded
  records.
- Normalized the article segment as a source-backed synthetic member with parent
  issue lineage, page-range evidence, OCR-like fixture text evidence, and safe
  article-scan access locators.
- Included the article fixture in demo corpus assembly, archive evals, and
  search-usefulness audit corpus assembly.
- Updated archive eval result-shape checks to recognize article/page/OCR-like
  evidence without weakening the hard task.
- Added focused connector, index/search, eval, source-registry, and hardening
  tests.

No live source behavior, OCR/PDF/image parser, real scan, copyrighted article
text, arbitrary local ingestion, external baseline, fuzzy/vector/LLM retrieval,
Rust port, native app, or deployment behavior was added.

