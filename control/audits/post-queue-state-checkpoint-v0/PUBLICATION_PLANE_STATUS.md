# Publication Plane Status

Publication inventories are present under `control/inventory/publication/` and validate successfully. `public_site/` remains the current GitHub Pages static artifact. The GitHub Pages workflow is configured for static `public_site/`, but this checkpoint did not check GitHub Actions run status and does not claim deployment success.

Generated public data exists under `public_site/data/`. Lite/text/files compatibility surfaces and static resolver demos are present. Custom-domain and alternate-host readiness is policy-only: no DNS, CNAME, or alternate host is configured.

Live backend handoff is contract-only. `/api/v1` is reserved/future, not live. Live Probe Gateway is policy-only and disabled; no live probes or external source calls are implemented.
