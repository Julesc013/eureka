# Rehearsal Scope

Public Search Rehearsal v0 is a local/prototype rehearsal only. It validates
that the local runtime and static handoff behave coherently under the governed
`local_index_only` mode.

The rehearsal did not deploy a hosted backend, modify provider configuration,
configure a custom domain, call live external sources, query Google or Internet
Archive, fetch external URLs, scrape sites, crawl sources, add downloads,
installers, uploads, accounts, telemetry, auth, native clients, relay runtime,
snapshot reader runtime, or production hosting behavior.

The static handoff remains honest: `site/dist/search.html` can point operators
toward local runtime instructions, but it must not claim hosted search exists
when no backend is configured.

## Runtime Boundary

- Mode: `local_index_only`
- Runtime: local/prototype backend only
- Static artifact: `site/dist`
- Hosted backend: unavailable
- Live probes: disabled
- Downloads, installs, uploads: disabled
- Local path search: disabled
- Telemetry/accounts: disabled

## Evidence Boundary

The primary evidence comes from `python scripts/public_search_smoke.py --json`,
static handoff validators, and contract validators. No external evidence was
fabricated.
