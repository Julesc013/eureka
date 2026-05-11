# H11 Storefront Live Probe Blocked Mode

H11 storefront live probes are approval-gated metadata observations for storefront, app-store, marketplace, product-listing, version, price, availability, review/rating, account-boundary, acquisition-surface, and rights/safety metadata.

Current status is fail-closed. Default CLI behavior is offline validation and dry preflight. If a committed source-specific approval is missing, the framework emits a blocked result and performs no external request.

## Boundaries

- Metadata-only outputs are candidates and previews, not truth.
- API/catalog/storefront/product-page lookup remains false unless an exact committed bounded metadata policy approves it.
- Downloads, account access, purchases, entitlement checks, installs, launches, review/rating writes, scraping, crawling, restricted-source access, and bypass behavior remain forbidden.
- Source-cache, evidence, and review outputs are previews/seeds only.
- Public index and master index mutation remain false.

## Validation

- `python scripts/validate_h11_storefront_live_probe.py`
- `python scripts/run_h11_storefront_live_probe.py --source-id fdroid_metadata --request-key example_app_metadata --check`
- `python scripts/summarize_h11_storefront_live_probe_outputs.py --input examples/connectors/h11_storefront/live_probe_results --check`
