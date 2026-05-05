# Public Search Boundary

Public search must not call npm live. Public search must not accept arbitrary package, scoped-package, or registry params for live fetch. Public search may later read public index/source cache summaries only after review. Public query params must not choose npm live mode. Public query params must not provide arbitrary package refs for live fetch. Public search result cards may show source cache/evidence refs only after future runtime and review. Static site must not claim live npm search until runtime and deployment evidence exist.
