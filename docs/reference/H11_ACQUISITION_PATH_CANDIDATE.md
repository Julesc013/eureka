# H11 Acquisition Path Candidate

H11-BUNDLE-02 is the fixture-only storefront/app-store runtime. It parses committed synthetic fixtures into normalized storefront records, listing identity candidates, app/product candidates, version/release/channel candidates, price/availability/region candidates, blocked acquisition path candidates, review/rating metadata candidates, blocked account/entitlement boundary candidates, rights/safety candidates, source-cache previews, evidence previews, and replay reports.

It is not a live connector, storefront query, product-page fetcher, downloader, account connector, purchase or entitlement tool, installer, launcher, review writer, scraper, crawler, bypass tool, source-cache writer, evidence accepter, review-queue writer, public-index mutator, master-index mutator, or production coverage claim.

All outputs remain candidates or previews. They do not accept listing truth, app/product truth, version truth, current price, current availability, acquisition permission, account or entitlement truth, review/rating quality truth, rights clearance, legal acquisition, installability, malware safety, content safety, privacy safety, verified authenticity, source truth, evidence truth, candidate truth, public truth, or master truth.

Validation commands:

- `python scripts/validate_h11_storefront_fixture_runtime.py`
- `python scripts/normalize_h11_storefront_fixture.py --source-id fdroid_metadata --input examples/connectors/h11_storefront/fixtures/fdroid_metadata/app_product_identity_record.json --check`
- `python scripts/replay_h11_storefront_fixtures.py --check`
- `python scripts/summarize_h11_storefront_fixture_outputs.py --input examples/connectors/h11_storefront --check`
