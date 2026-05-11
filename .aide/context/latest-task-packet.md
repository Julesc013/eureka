# AIDE Latest Task Packet

## PHASE

H12-BUNDLE-01 - Retro and community archive source-family policy packs

## GOAL

Start H12 by adding policy-pack-only governance for retro/community archive source families after H11 storefront/app-store review closeout. Main development lane proceeds to H12-BUNDLE-01 after H11-BUNDLE-04; HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## WHY

H11-BUNDLE-04 closed the storefront/app-store wave with fixture-equivalent review integration, quality delta, postmortem, and a next-phase recommendation of READY_FOR_H12_BUNDLE_01. H12 should define source-family policy packs only and must not enable live access, downloads, scraping, crawling, source sync, index mutation, evidence acceptance, candidate acceptance, or truth acceptance.

## CONTEXT_REFS

- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/reports/eureka-repo-health.md`
- `.aide/queue/H12-BUNDLE-01/task.yaml`
- `control/audits/h11-bundle-04-storefront-review-quality-audit-v0/`
- `control/audits/h11-bundle-03-storefront-live-probes-v0/`
- `control/audits/h11-bundle-02-storefront-fixture-runtime-v0/`
- `control/audits/h11-bundle-01-storefront-policy-packs-v0/`
- `AGENTS.md`

## ALLOWED_PATHS

- `.aide/`
- H12-BUNDLE-01 governed policy-pack artifacts only when that queue item is explicitly started from its task packet.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- `site/dist/**`
- `data/public_index/**`
- master-index roots
- local private roots
- account, receipt, entitlement, storefront library, app download, package download, checkout/session, install/launch/action, restricted-source, hosted config, provider secret, or telemetry roots

## IMPLEMENTATION

- Read H11-BUNDLE-04 audit outputs and next-phase recommendation first.
- Keep H12 work policy-pack-only unless a future reviewed packet explicitly broadens scope.
- Do not perform new live calls or infer operator signoff.
- Do not accept source, evidence, candidate, archive identity, availability, acquisition, rights/safety, public, or master truth.

## VALIDATION

- `.aide/scripts/aide_lite.py doctor`
- `.aide/scripts/aide_lite.py validate`
- `.aide/scripts/aide_lite.py test`
- `.aide/scripts/aide_lite.py selftest`
- `.aide/scripts/aide_lite.py eval run`
- `.aide/scripts/aide_lite.py verify`
- `scripts/check_architecture_boundaries.py`
- `python scripts/validate_h11_storefront_review_quality_audit.py`
- `python scripts/validate_h11_storefront_live_probe.py`
- `python scripts/validate_h11_storefront_fixture_runtime.py`
- `python scripts/validate_h11_storefront_policy_packs.py`
- `python -m unittest discover -s tests -t .`

## EVIDENCE

- H11-BUNDLE-04 audit pack under `control/audits/h11-bundle-04-storefront-review-quality-audit-v0/`
- H11 review integration examples under `examples/connectors/h11_storefront/review_integration/`
- H11 live-probe blocked reports under `examples/connectors/h11_storefront/live_probe_results/`
- Validation command results and commit hash from the completed task.

## NON_GOALS

- No Eureka product behavior change.
- No live source calls, network calls, model/provider calls, source sync, downloads, account access, purchases, entitlement checks, installs, launches, review/rating writes, scraping, crawling, restricted-source access, bypass, public index mutation, master index mutation, hosting, uploads, telemetry, or truth acceptance.
- Do not rely on full chat history; use compact repo-local refs.

## ACCEPTANCE

- H12-BUNDLE-01 can start from H11 fixture-equivalent review outputs.
- J1 risky actions, K semantic/AI, and L wider clients remain deferred.
- Validation is run and recorded honestly.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4222
- approx_tokens: 1056
- budget_status: PASS
- formal ledger: `.aide/reports/token-ledger.jsonl`
