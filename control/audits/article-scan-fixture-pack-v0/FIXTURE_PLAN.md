# Fixture Plan

The implementation adds one active recorded fixture source:

- `article-scan-recorded-fixtures`
- source family: `article_scan_recorded`
- posture: `active_recorded_fixture`
- coverage depth: `content_or_member_indexed`

Fixture shape:

- parent issue: `PC Magazine July 1994 Issue Fixture`
- article segment: `Article inside 1994 magazine scan about ray tracing - Ray
  Tracing on the Desktop`
- topic: `ray tracing`
- page range: `123-128`
- member path:
  `articles/ray-tracing-on-the-desktop/pages-123-128.ocr.txt`
- payloads:
  `pc_magazine_1994_issue_manifest.json` and
  `pc_magazine_1994_ray_tracing_ocr.txt`

All payload text is synthetic fixture text. The payloads are tiny and
text-safe, contain no real magazine scan, and contain no copied article text.

