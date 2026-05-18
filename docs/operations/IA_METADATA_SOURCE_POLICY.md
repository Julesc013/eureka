# IA Metadata Source Policy

IA-00 approves policy only. It does not approve live calls.

## Allowed Later

After IA-01 fixture replay and explicit IA-02 operator approval, a local pilot
may use these metadata-only endpoint classes:

- bounded metadata search with a small row cap
- exact item metadata read by identifier
- exact item file-list metadata read by identifier

All future live calls require a descriptive User-Agent, operator-configured
contact, timeout, finite retry budget, conservative backoff, Retry-After
handling, cache-before-repeat behavior, row/page caps, and a fail-closed kill
switch checked before every request.

## Forbidden

The following remain forbidden:

- downloads, item file fetches, media file fetches
- uploads and write APIs
- S3-style APIs
- authenticated account APIs
- reviews/write APIs and tasks/write APIs
- broad collection crawl
- unbounded paging
- public query fanout
- arbitrary URL fetch
- Wayback content replay
- page scraping outside the documented metadata/API posture
- source-cache writes in IA-00
- evidence writes in IA-00
- candidate, reviewed, or master index mutation in IA-00
- production deployment or public launch claims

## Data Use

Metadata is source observation material only. It may be cached later only after
IA-03 approval, may produce evidence candidates only after IA-04 approval, and
may reach reviewed local index integration only after review and later index
gates.

No IA metadata field creates accepted truth by itself.
