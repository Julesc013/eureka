# Local Source Cache Privacy And Risk Policy

The local source cache planning layer treats source observations as potentially
sensitive until reviewed. It is not a telemetry feature and does not collect
public user search history.

## Privacy Boundary

Current planning artifacts must not store secrets, credentials, account
sessions, private user files, telemetry streams, private paths, cookies, API
keys, tokens, or source payloads from live access.

Future local source-cache roots are documented for planning only and are not
created by B-13. A future runtime task must define deletion/reset behavior,
private-root ownership, and operator controls before creating any private state.

## Rights And Content Risk

Source-cache records cannot claim:

- rights clearance
- malware safety
- verified installability
- exhaustive global search
- production readiness

Unreviewed executable payloads, binary downloads, installer payloads, package
artifacts, mirrors, raw crawls, and replayed archived content are out of scope.

## Poisoning And Access Risk

Future source access must guard against source manipulation, search result
scraping, rank manipulation, arbitrary URL injection, account/session leakage,
payload substitution, stale metadata, and identity confusion.

Current planning examples are synthetic and repo-local. They do not include
live results, scraped pages, downloadable binaries, external API payloads, or
private local state.

## Evidence Boundary

Source-cache output may become an evidence candidate only through a future
bridge and review task. It must not become accepted evidence, accepted public
record, public index material, or master-index material automatically.
