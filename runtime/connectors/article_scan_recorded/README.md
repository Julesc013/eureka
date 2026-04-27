# Article Scan Recorded Fixtures Connector

This connector replays a tiny committed article/scan-shaped fixture. It is
recorded fixture coverage only:

- no live source calls
- no scraping or crawling
- no OCR engine
- no PDF or image parsing
- no real magazine scans
- no copyrighted article text

The fixture exists to exercise one hard eval shape: an article-like segment
inside a scanned magazine-like parent item with a page range, source lineage,
and synthetic OCR-like text. The payload text is deliberately synthetic and
text-safe; it is not a real article and does not imply broad article search.
