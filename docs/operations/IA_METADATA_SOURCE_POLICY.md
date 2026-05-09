# IA Metadata Source Policy

Current status: `fixture_only`.

Internet Archive is classified as a preservation/source-metadata provider, not
canonical truth. IA-BUNDLE-01 does not approve live source access.

## Pending Operator Decisions

- User-Agent
- contact policy
- allowed endpoints
- forbidden endpoint review
- requests per minute
- timeout
- retry/backoff
- cache TTL
- kill switch

## Current Denials

- no Internet Archive calls
- no metadata live probe
- no file download
- no item file fetch
- no scraping
- no crawling
- no login/session use
- no public-query live fanout
- no source-cache runtime write
- no evidence-ledger runtime write
- no public/master index mutation

## Next Gate

IA-BUNDLE-02 may request a bounded metadata-only live probe only after the
operator/source policy decisions are explicit and reviewed.
