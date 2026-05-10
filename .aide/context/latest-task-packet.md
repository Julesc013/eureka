# AIDE Latest Task Packet

## PHASE

H6-BUNDLE-01 - Web archive, news, and event source-family policy packs

## GOAL

Prepare the next Eureka H6 task after H5-BUNDLE-04. This packet is a compact
AIDE resumption handoff only; it does not itself authorize live source calls,
scraping, crawling, source sync, downloads, browser automation, provider/model
calls, public/master index mutation, truth acceptance, hosting, deployment, or
changing Eureka product behavior.

H6-BUNDLE-01 should define policy-pack-only source-family structure for web
archive, news, and event metadata sources. It should reuse the H0-H5 Source OS
patterns and treat all source observations, candidates, and packs as
review-gated previews until later gates explicitly open.

HUMAN-OBS-REVIEW-01 remains preserved as a parallel side-lane and is not
completed, promoted, or replaced by this H6 handoff.

## WHY

H5-BUNDLE-04 closed the vendor/update/driver wave with review integration,
quality delta, a connector wave postmortem, an integration audit, and a next
phase recommendation of `READY_FOR_H6_BUNDLE_01`.

H5 live probes remain approval-blocked. H5 fixture replay and blocked live-probe
outputs are sufficient for H5 closeout but do not approve any future live
access.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/H5-BUNDLE-04/task.yaml`
- `.aide/queue/H6-BUNDLE-01/task.yaml`
- `control/audits/h5-bundle-04-vendor-update-review-quality-audit-v0/`
- `control/audits/h5-bundle-03-vendor-update-live-probes-v0/`
- `control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/`
- `control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/`
- `docs/operations/H5_TO_H6_HANDOFF.md`
- `docs/operations/H5_TO_J1_K_L_DEFERRAL.md`

## ALLOWED_PATHS

- `.aide/**`
- H6 policy-pack contracts, source-pack policies, source records,
  connector-family mappings, approval gates, output/truth/no-live-call policies,
  examples, docs, validators, tests, audit pack, and bounded AIDE metadata only
  after an explicit H6-BUNDLE-01 prompt.

## IMPLEMENTATION

- Do not start H6-BUNDLE-01 implementation from this packet alone.
- Reuse Source OS policy, fixture, live-boundary, review, quality, postmortem,
  and audit patterns from H0-H5.
- Preserve no-live-call, no-scrape, no-crawl, no-download, no-source-sync,
  no-index-mutation, and no-truth-acceptance boundaries.
- Treat web archive, news, and event metadata as source observation material,
  not accepted public truth.
- Keep J1 risky actions, K semantic/AI, and L wider clients deferred unless a
  future reviewed gate explicitly opens them.

## ACCEPTANCE

- Latest handoff points to H6-BUNDLE-01.
- H5-BUNDLE-04 evidence remains reviewable.
- H6-BUNDLE-01 must not make live source calls by default.
- No Eureka product behavior change is authorized by this handoff.
- No live calls, scraping, crawling, downloads, source sync, public/master index
  mutation, evidence acceptance, candidate acceptance, source truth acceptance,
  public truth creation, hosting, deployment, or production-readiness claims are
  authorized.

## VALIDATION

- H5 closeout validator: `python scripts/validate_h5_vendor_update_review_quality_audit.py`
- H5 audit: `python scripts/audit_h5_vendor_update_driver_wave.py --check`
- Existing H5/H4/H3/H2/H1/H0/core validators
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- AIDE Lite: `.aide/scripts/aide_lite.py doctor`; `.aide/scripts/aide_lite.py validate`; `.aide/scripts/aide_lite.py test`; `.aide/scripts/aide_lite.py selftest`; `.aide/scripts/aide_lite.py eval run`; `.aide/scripts/aide_lite.py verify`; review-pack; adapter validate

## EVIDENCE

- `.aide/queue/index.yaml`
- `.aide/queue/H5-BUNDLE-04/task.yaml`
- `.aide/queue/H6-BUNDLE-01/task.yaml`
- `control/audits/h5-bundle-04-vendor-update-review-quality-audit-v0/h5_bundle_04_report.json`
- `control/audits/h5-bundle-04-vendor-update-review-quality-audit-v0/h5_exit_gate_decision.md`
- `control/audits/h5-bundle-04-vendor-update-review-quality-audit-v0/next_phase_recommendation.md`
- `examples/connectors/h5_vendor_update_driver/review_integration/`

## NON_GOALS

- No live calls, API calls, provider/model calls, browser automation, scraping,
  crawling, catalog sync, downloads, installs, execution, vendor tool
  invocation, package manager invocation, firmware flashing, source sync, public
  query fanout, public/master index mutation, evidence acceptance, candidate
  acceptance, source truth acceptance, identity truth acceptance, compatibility
  truth acceptance, authenticity truth acceptance, safety truth acceptance,
  public truth creation, public launch, deployment, or production-readiness
  claims.

## OUTPUT_SCHEMA

Future H6-BUNDLE-01 responses should preserve status, summary, commits, changed
paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1200
- budget_status: within_budget

## FORBIDDEN_PATHS

- `surfaces/**`
- `runtime/**`
- `contracts/**`
- `connectors/**`
- `native/**`
- `crates/**`
- `packaging/**`
- `third_party/**`
- `site/**`
- `site/dist/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`
- provider secret files
- package cache roots
- vendor download roots
- firmware staging roots
- repository clone roots
- repository mirror roots
