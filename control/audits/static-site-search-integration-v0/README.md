# P56 Static Site Search Integration v0

P56 integrates the generated static publication site with Eureka's public search
path while keeping GitHub Pages static-only and backend status honest.

The static site now exposes a no-JS search front door, lite/text/files search
surfaces, `data/search_config.json`, and `data/public_index_summary.json`.
Default status is backend unconfigured because no verified hosted backend URL
exists in repo evidence.

Non-goals: hosted backend deployment, live probes, source connector runtime,
external source calls, scraping, telemetry, accounts, uploads, downloads,
installers, AI runtime, arbitrary URL fetching, index mutation, pack import,
staging runtime, or production readiness.
