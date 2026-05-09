# IA Metadata No-Live-Call Policy

IA-BUNDLE-01 forbids all external source access.

## Forbidden

- Internet Archive live calls
- external URL calls
- API calls
- live probes
- source sync
- live connector runtime
- downloads
- item file fetches
- scraping
- crawling
- arbitrary URL fetch
- browser automation
- model/provider calls
- public-query fanout
- source cache runtime mutation
- evidence ledger runtime mutation
- public/master index mutation

## Enforcement

The normalizer imports only standard-library local JSON/path utilities. The
validator checks for network-capable imports, verifies all live/source/product
boundary booleans remain false, and rejects fixtures that claim live calls,
downloads, public-index mutation, master-index mutation, rights clearance,
malware safety, or verified installability.
