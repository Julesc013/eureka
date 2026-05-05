# Public Search Boundary

- Public search must not call Software Heritage live.
- Public search must not accept arbitrary SWHID/origin/repository params for live fetch.
- Public search may later read public index/source cache summaries only after review.
- Public query params must not choose Software Heritage live mode.
- Public query params must not provide arbitrary SWHID/origin/repository refs for live fetch.
- Public search result cards may show source cache/evidence refs only after future runtime and review.
- Static site must not claim live Software Heritage search until runtime and deployment evidence exist.
