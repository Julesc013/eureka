# Static Site Search Integration

P56 makes the static site a search front door without pretending a backend is
live.

## Current Mode

The default mode is backend unconfigured. `search.html`, `lite/search.html`,
`text/search.txt`, and `files/search.README.txt` explain that Eureka has a
local_index_only public search runtime and a generated public index, but no
verified hosted backend URL is configured for the static site.

The generated static data files are:

- `data/search_config.json`
- `data/public_index_summary.json`

## No-JS Baseline

The search page is no-js compatible. When no verified backend exists, hosted
form submission is disabled and the page shows local runtime instructions
instead:

```powershell
python scripts/run_hosted_public_search.py --check-config
python scripts/run_hosted_public_search.py --host 127.0.0.1 --port 8080
```

## Verified Backend Mode

A future hosted backend URL may be configured only after operator evidence
records the deployed URL, commit SHA, environment, and route checks. Until that
happens, `hosted_backend_verified` must remain false and
`search_form_enabled` must remain false.

## Safety

The static handoff keeps:

- no live probes
- no downloads
- no uploads
- no accounts
- no installers
- no local path access
- no arbitrary URL fetching
- no AI runtime
- no production claim

P57 expands public search safety evidence and checks this static handoff stays
honest: backend unconfigured by default, no fake hosted URL, no live probes,
and no downloads/uploads/local paths/arbitrary URL fetch. P58 may rehearse
hosted search only after an operator-hosted wrapper URL and evidence exist.
## P58 Hosted Rehearsal Compatibility

P58 checks that the static search handoff remains backend-unconfigured while
the hosted wrapper is rehearsed locally. `search_config.json` still has no
verified hosted backend URL, and static form submission remains disabled until
operator deployment evidence exists.

## Query Intelligence Boundary

P59 Query Observation, P60 Shared Query/Result Cache, P61 Search Miss Ledger,
and P62 Search Need Record remain contract-only. Static search pages do not
collect observations, write cache entries, write miss ledger entries, create
search needs, claim demand counts, enqueue probes, mutate indexes, or publish
public demand counts.

P63 Probe Queue also remains contract-only. Static search pages do not create
probe queue items, execute probes, call live sources, mutate source caches,
mutate evidence ledgers, mutate candidate indexes, or change hosted-backend
verification status.
## P64 Candidate Index Note

Static search handoff remains honest about backend state. P64 candidate records
are contract-only and are not included in static search config, result ranking,
public index summaries, or backend URL handoff.
