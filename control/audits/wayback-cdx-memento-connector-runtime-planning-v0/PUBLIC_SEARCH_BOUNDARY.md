# Public Search Boundary

Public search must not call Wayback/CDX/Memento live.

Public search must not accept arbitrary URL parameters for live fetch. Public query parameters must not choose Wayback/CDX/Memento live mode, source roots, connector paths, source-cache paths, evidence-ledger paths, URI-R values for live fetch, capture identifiers, URLs, or filesystem roots.

Future public search may read reviewed public-index or source-cache summaries only after a separate runtime and review process. Result cards may show source-cache or evidence refs only after future runtime, review, and public-safe projection. Static site output must not claim live Wayback/CDX/Memento search until runtime and deployment evidence exist.
