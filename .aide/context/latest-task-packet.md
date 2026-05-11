# AIDE Latest Task Packet

## PHASE

H11-BUNDLE-04 - Storefront and app-store review integration and quality delta

## GOAL

Integrate H11 storefront/app-store policy, fixture, and blocked live-probe outputs into review/quality previews only. Main development lane proceeds to H11-BUNDLE-04 after H11-BUNDLE-03; HUMAN-OBS-REVIEW-01 is a parallel side-lane.

## WHY

H11-BUNDLE-03 added the fail-closed bounded metadata-only live-probe framework. No operator live approvals are committed, so H11-BUNDLE-04 should use committed H11 policy packs, fixture replay outputs, and blocked live-probe reports as fixture-equivalent review material.

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
- `.aide/queue/H11-BUNDLE-04/task.yaml`
- `control/audits/h11-bundle-03-storefront-live-probes-v0/`
- `control/audits/h11-bundle-02-storefront-fixture-runtime-v0/`
- `control/audits/h11-bundle-01-storefront-policy-packs-v0/`
- `AGENTS.md`

## ALLOWED_PATHS

- `.aide/`
- H11-BUNDLE-04 governed review-integration artifacts only when that queue item is explicitly started from its task packet.

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

- Read H11-BUNDLE-03 audit outputs and fixture-equivalent results first.
- Keep outputs as review seeds, previews, scorecards, quality deltas, and postmortems only.
- Do not perform new live calls or infer operator signoff.
- Do not accept source, evidence, candidate, listing, app/product, version, price/availability, acquisition, review/rating, account/entitlement, rights/safety, public, or master truth.

## VALIDATION

- `.aide/scripts/aide_lite.py doctor`
- `.aide/scripts/aide_lite.py validate`
- `.aide/scripts/aide_lite.py test`
- `.aide/scripts/aide_lite.py selftest`
- `.aide/scripts/aide_lite.py eval run`
- `.aide/scripts/aide_lite.py verify`
- `scripts/check_architecture_boundaries.py`
- `python scripts/validate_h11_storefront_live_probe.py`
- `python scripts/validate_h11_storefront_fixture_runtime.py`
- `python scripts/validate_h11_storefront_policy_packs.py`
- `python -m unittest discover -s tests -t .`

## EVIDENCE

- H11-BUNDLE-03 audit pack under `control/audits/h11-bundle-03-storefront-live-probes-v0/`
- H11 live-probe result examples under `examples/connectors/h11_storefront/live_probe_results/`
- H11 live-probe output previews under `examples/connectors/h11_storefront/live_probe_outputs/`
- Validation command results and commit hash from the completed task.

## NON_GOALS

- No Eureka product behavior change.
- No live source calls, network calls, model/provider calls, source sync, downloads, account access, purchases, entitlement checks, installs, launches, review/rating writes, scraping, crawling, restricted-source access, bypass, public index mutation, master index mutation, hosting, uploads, telemetry, or truth acceptance.
- Do not rely on full chat history; use compact repo-local refs.

## ACCEPTANCE

- H11-BUNDLE-04 can start from fixture-equivalent H11 outputs.
- HUMAN-OBS-REVIEW-01 remains documented as a parallel side-lane.
- Validation is run and recorded honestly.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 4230
- approx_tokens: 1058
- budget_status: PASS
- formal ledger: `.aide/reports/token-ledger.jsonl`
