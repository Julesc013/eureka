# AIDE Latest Task Packet

## PHASE

H11-BUNDLE-03 - Storefront and app-store approved metadata-only live probes. HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## GOAL

Continue H11 by adding approval-gated, bounded, metadata-only live-probe envelopes after H11-BUNDLE-02 fixture runtimes and normalizers.

## WHY

H11-BUNDLE-02 added fixture-only storefront/app-store normalization and replay for 16 sources. It validated without live calls, API/catalog queries, storefront searches, product-page fetches, downloads, account access, purchase automation, entitlement checks, install/launch actions, review/rating writes, scraping, crawling, source sync, public/master index mutation, or truth acceptance.

## CONTEXT_REFS

- `control/audits/h11-bundle-02-storefront-fixture-runtime-v0/`
- `control/audits/h11-bundle-01-storefront-policy-packs-v0/`
- `contracts/connectors/h11_storefront_fixture.v0.json`
- `contracts/connectors/h11_storefront_normalized_record.v0.json`
- `runtime/connectors/h11_storefront/`
- `examples/connectors/h11_storefront/fixtures/`
- `examples/connectors/h11_storefront/normalized/`
- `examples/connectors/h11_storefront/replay_results/`
- `docs/operations/H11_STOREFRONT_FIXTURE_REPLAY.md`
- `docs/operations/H11_STOREFRONT_FIXTURE_NO_LIVE_CALL_POLICY.md`
- `docs/operations/H11_STOREFRONT_FIXTURE_NO_PURCHASE_DOWNLOAD_ACCOUNT_POLICY.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/memory/project-state.md`
- `AGENTS.md`

## ALLOWED_PATHS

H11 storefront/app-store live-probe policies, allowed request manifests, endpoint/request/output/path/truth policies, source-specific metadata-only wrappers, scripts, examples, docs, tests, audit pack, and `.aide/` operating metadata when explicitly scoped.

## FORBIDDEN_PATHS

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

Use H11-BUNDLE-01 policies and H11-BUNDLE-02 fixtures as governance input. Default behavior must be offline validation and dry preflight. Do not infer operator signoff; any live call requires exact committed source-specific approval and bounded metadata-only request manifests.

## VALIDATION

Run H11 live-probe validators when added, H11 fixture and policy validators, architecture checks, and AIDE Lite checks where practical:

- `python scripts/validate_h11_storefront_fixture_runtime.py`
- `python scripts/validate_h11_storefront_policy_packs.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/h11-bundle-02-storefront-fixture-runtime-v0/`
- `.aide/queue/H11-BUNDLE-03/task.yaml`

## ACCEPTANCE

H11 live probes remain fail-closed unless exact source-specific approval exists. No source sync, downloads, account access, purchase/download/install/launch behavior, public/master index mutation, or truth acceptance may occur. The next task must preserve no Eureka product behavior change.

## NON_GOALS

No broad storefront search, unbounded API use, source sync, downloads, uploads, account access, purchase automation, entitlement checks, install/launch actions, review/rating writes, scraping, crawling, bypass, restricted-source access, public/master index mutation, product behavior changes, or model/provider calls.

## OUTPUT_SCHEMA

Return a compact final report with status, summary, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- approx_tokens: 1000
