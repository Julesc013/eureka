# Local Auto-Search Suites

LOCAL-10 uses a fixed query list so search behavior can be reproduced.

Built-in queries:

- `sampleproject`
- `definitely-not-present-local-10`
- `visual studio 2008 express`
- `old printer driver windows xp`
- `mac os 9 utility`
- `query with <unsafe> chars`
- an overlong query generated in code

The suite calls `/api/v1/search` for each query. Missing-result cases also call
`/api/v1/absence`. Overlong queries may pass by returning either a bounded
search result or a bounded validation error.

The suite does not generate synthetic queries, run source probes, perform live
source search, crawl, scrape, download, execute, or call a model provider.
