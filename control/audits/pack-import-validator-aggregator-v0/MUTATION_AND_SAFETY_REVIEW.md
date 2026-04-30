# Mutation And Safety Review

The aggregate validator performs no mutation.

Explicitly false:

- `mutation_performed`
- `import_performed`
- `staging_performed`
- `indexing_performed`
- `network_performed`

The command does not create staging directories, write import reports, mutate
local indexes, mutate canonical source/evidence/index records, upload packs,
submit contributions, write a master index, open sockets, fetch URLs, scrape,
crawl, load executable plugins, download artifacts, install software, or run
payloads.

Validator success is not rights clearance, malware safety, canonical truth,
compatibility truth, public-search eligibility, master-index acceptance, or
production readiness.

