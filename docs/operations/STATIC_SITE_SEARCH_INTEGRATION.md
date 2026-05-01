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

P57 should expand public search safety evidence. P58 may rehearse hosted search
only after an operator-hosted wrapper URL and evidence exist.
