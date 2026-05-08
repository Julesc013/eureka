# Local Evidence Ledger Privacy And Risk Policy

The local evidence ledger planning layer treats evidence candidates and
provenance links as sensitive until reviewed. It is not a telemetry feature and
does not collect public user search history.

## Privacy Boundary

Current planning artifacts must not store secrets, credentials, account
sessions, private user files, telemetry streams, private paths, cookies, API
keys, tokens, raw external payloads, or live source results.

Future local evidence-ledger roots are documented for planning only and are not
created by B-14. A future runtime task must define deletion/reset behavior,
private-root ownership, correction records, supersession records, and operator
controls before creating local private state.

## Rights And Content Risk

Evidence ledger records cannot claim:

- rights clearance
- malware safety
- verified installability
- exhaustive global search
- production readiness

Unreviewed executable payloads, binary downloads, installer payloads, package
artifacts, mirrors, raw crawls, and replayed archived content are out of scope.

## Poisoning And Claim Risk

Future evidence handling must guard against source manipulation, arbitrary URL
injection, account/session leakage, stale metadata, identity confusion, checksum
overclaim, compatibility overclaim, AI draft overclaim, contribution overclaim,
and conflict suppression.

Current planning examples are synthetic and repo-local. They do not include
live results, scraped pages, downloadable binaries, external API payloads, or
private local state.

## Evidence Boundary

Evidence candidates may become reviewed evidence only through future review and
promotion tasks. They must not become accepted public records, public index
material, or master-index material automatically.
