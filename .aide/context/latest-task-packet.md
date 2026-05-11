# AIDE Latest Task Packet

## PHASE

H11-BUNDLE-02 - Storefront and app-store fixture runtimes and normalizers. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Continue H11 by adding fixture-only storefront/app-store normalization and replay outputs after H11-BUNDLE-01 policy packs.

## WHY

H11-BUNDLE-01 added policy-pack-only storefront, app-store, marketplace, product listing, availability, account/auth, acquisition-surface, review/rating, and rights/safety governance. It validated offline without enabling live calls, storefront queries, product-page fetches, downloads, account access, purchase automation, entitlement checks, install/launch actions, scraping, crawling, source sync, public/master index mutation, or truth acceptance.

## CONTEXT_REFS

- `control/audits/h11-bundle-01-storefront-policy-packs-v0/`
- `control/inventory/source_packs/h11_storefront_sources.json`
- `control/inventory/source_packs/h11_storefront_source_pack_policy.json`
- `examples/connectors/h11_storefront/`
- `examples/source_packs/h11_storefront_source_pack_manifest_v0.json`
- `docs/operations/H11_STOREFRONT_FIXTURE_PLAN.md`
- `docs/operations/H11_STOREFRONT_NO_LIVE_CALL_POLICY.md`
- `docs/operations/H11_STOREFRONT_NO_PURCHASE_DOWNLOAD_ACCOUNT_POLICY.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/memory/project-state.md`
- `AGENTS.md`

## ALLOWED_PATHS

H11 storefront fixture contracts, committed public-safe fixtures, fixture normalizers, replay scripts, examples, docs, tests, audit pack, and `.aide/` operating metadata only when the next reviewed task explicitly scopes them.

## FORBIDDEN_PATHS

- live connector runtime enablement
- product search/public surfaces
- runtime/**
- contracts/**
- surfaces/**
- site/dist
- site/**
- native/**
- crates/**
- connectors/**
- packaging/**
- third_party/**
- data/public_index
- master-index or publication roots
- storefront account/session roots
- receipt, entitlement, store-library, app-download, package-download, game-install, checkout/session, upload, or private local roots
- hosted behavior
- native/client behavior

## IMPLEMENTATION

Use H11-BUNDLE-01 source records and policy packs as governance input only. Fixtures must be committed synthetic or public-safe records. Do not access accounts, receipts, tokens, user libraries, purchase history, license keys, subscriptions, device registrations, paid APIs, storefronts, product pages, or downloads.

## VALIDATION

Run H11 fixture validators when added, H11 policy-pack validator, architecture checks, and AIDE Lite checks where practical:

- `python scripts/validate_h11_storefront_policy_packs.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/h11-bundle-01-storefront-policy-packs-v0/`
- `.aide/queue/H11-BUNDLE-02/task.yaml`

## ACCEPTANCE

H11 fixture runtime remains fixture-only and must proceed with no Eureka product behavior change. No live source access, account access, purchase/download/install/launch behavior, public/master index mutation, or truth acceptance may occur.

## NON_GOALS

No live source calls, API/catalog/storefront queries, product-page fetches, screenshot/media fetches, downloads, uploads, account access, purchase automation, checkout/cart/wishlist/redemption/subscription automation, entitlement checks, install/launch actions, review/rating writes, scraping, crawling, bypass, restricted-source access, source sync, public/master index mutation, product behavior changes, or model/provider calls.

## OUTPUT_SCHEMA

Return a compact final report with status, summary, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 900
