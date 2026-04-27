# Hard Eval Impact

Baseline:

- `capability_gap=1`
- `satisfied=5`
- remaining capability gap: `article_inside_magazine_scan`

Current result:

- `satisfied=6`

`article_inside_magazine_scan` is satisfied under the current strict checks
because the primary candidate is an article-like synthetic member with:

- source id `article-scan-recorded-fixtures`
- source family `article_scan_recorded`
- parent issue lineage
- member path
  `articles/ray-tracing-on-the-desktop/pages-123-128.ocr.txt`
- page range `123-128`
- topic evidence for `ray tracing`
- OCR-like fixture text evidence
- lane/user-cost evidence identifying it as a lower-cost member/segment result

This is not a broad article search or OCR capability. It is one bounded
fixture-backed example.

