# AIDE Latest Task Packet

## PHASE

H5-BUNDLE-04 - Vendor/update/driver review integration and quality delta

## GOAL

Prepare the next Eureka H5 task after H5-BUNDLE-03. This packet is a compact
AIDE resumption handoff only; it does not itself authorize new live source
calls, catalog fetching, downloads, vendor tool invocation, package manager
invocation, installer execution, firmware flashing, source sync, public/master
index mutation, truth acceptance, or changing Eureka product behavior.

H5-BUNDLE-04 should integrate committed H5 fixture replay outputs and the
H5-BUNDLE-03 blocked live-probe reports into review seeds, quality delta,
connector scorecards, source-pack previews, postmortem evidence, H5 exit
decision material, and the next-phase recommendation.

HUMAN-OBS-REVIEW-01 remains preserved as a parallel side-lane and is not
completed, promoted, or replaced by this H5 handoff.

## WHY

H5-BUNDLE-03 added fail-closed metadata-only live-probe contracts, policies,
source wrappers, CLI, validator, summary tooling, examples, tests, docs, and
audit evidence for fifteen H5 vendor/update/driver sources. No source has
committed live approval, so live-probe outputs are blocked preflight reports
with `request_count: 0` and `network_used: false`.

H5-BUNDLE-02 fixture replay outputs remain the fixture-equivalent review input.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/H5-BUNDLE-03/task.yaml`
- `.aide/queue/H5-BUNDLE-04/task.yaml`
- `control/audits/h5-bundle-03-vendor-update-live-probes-v0/`
- `control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/`
- `contracts/connectors/h5_vendor_update_live_probe_*.v0.json`
- `contracts/connectors/h5_vendor_update_*candidate*.v0.json`
- `runtime/connectors/h5_vendor_update_driver/`
- `examples/connectors/h5_vendor_update_driver/`
- `docs/operations/H5_VENDOR_UPDATE_LIVE_PROBE_*.md`

## ALLOWED_PATHS

- `.aide/**`
- `contracts/connectors/h5_vendor_update_live_probe_*.v0.json`
- `contracts/connectors/h5_vendor_update_connector_health_summary.v0.json`
- `control/inventory/connectors/h5_vendor_update_live_probe_*.json`
- `runtime/connectors/h5_vendor_update_driver/live_probe*.py`
- `scripts/*h5_vendor_update_live_probe*.py`
- `scripts/validate_h5_vendor_update_driver_fixture_runtime.py`
- `examples/connectors/h5_vendor_update_driver/live_probe*/**`
- `tests/**/test_h5_vendor_update_live_probe*.py`
- `docs/reference/H5_VENDOR_UPDATE_LIVE_PROBE*.md`
- `docs/reference/H5_VENDOR_UPDATE_CONNECTOR_HEALTH_SUMMARY.md`
- `docs/architecture/H5_VENDOR_UPDATE_LIVE_PROBE_MODEL.md`
- `docs/operations/H5_VENDOR_UPDATE_LIVE_PROBE_*.md`
- `control/audits/h5-bundle-03-vendor-update-live-probes-v0/**`
- H5 review integration and quality-delta contracts, policies, runtime helpers,
  scripts, examples, docs, tests, and audit paths only if a future prompt
  explicitly scopes H5-BUNDLE-04.

## IMPLEMENTATION

- Do not start H5-BUNDLE-04 implementation from this packet alone.
- Use H5-BUNDLE-02 fixture replay outputs plus H5-BUNDLE-03 blocked reports.
- Do not invent live evidence or operator approval.
- Preserve fail-closed behavior for every source.
- Preserve no-catalog-sync, no-download, no-install, no-execute,
  no-firmware-flash, no-source-sync, no-index-mutation, and
  no-truth-acceptance boundaries.
- Treat vendor identity, driver identity, firmware/update identity, runtime
  identity, device compatibility, payload/hash/signature metadata, source-cache,
  evidence, and review outputs as candidates/previews/seeds only.

## ACCEPTANCE

- Latest handoff points to H5-BUNDLE-04.
- H5-BUNDLE-03 evidence remains reviewable.
- H5-BUNDLE-04 must not make new live source calls by default.
- No Eureka product behavior change is authorized by this handoff.
- No live calls, catalog sync/fetch, downloads, vendor tool invocation, package
  manager invocation, firmware flashing, installs, execution, source sync,
  public/master index mutation, evidence acceptance, candidate acceptance,
  source truth acceptance, vendor/driver/firmware/runtime identity truth
  acceptance, compatibility truth acceptance, authenticity truth acceptance,
  safety truth acceptance, rights clearance, malware safety, installability,
  hosting, deployment, or production-readiness claims are authorized.

## VALIDATION

- `python scripts/validate_h5_vendor_update_live_probe.py`
- `python scripts/run_h5_vendor_update_live_probe.py --source-id nvidia_driver_downloads --request-key example_driver_metadata --check`
- `python scripts/summarize_h5_vendor_update_live_probe_outputs.py --input examples/connectors/h5_vendor_update_driver/live_probe_results --check`
- H5 live-probe targeted unit tests
- H5 fixture and policy validators
- Existing H4/H3/H2/H1/H0/core validators
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- AIDE Lite: `.aide/scripts/aide_lite.py doctor`; `.aide/scripts/aide_lite.py validate`; `.aide/scripts/aide_lite.py test`; `.aide/scripts/aide_lite.py selftest`; `.aide/scripts/aide_lite.py eval run`; `.aide/scripts/aide_lite.py verify`; review-pack; adapter validate

## EVIDENCE

- `.aide/queue/index.yaml`
- `.aide/queue/H5-BUNDLE-03/task.yaml`
- `.aide/queue/H5-BUNDLE-04/task.yaml`
- `control/audits/h5-bundle-03-vendor-update-live-probes-v0/h5_bundle_03_report.json`
- `control/audits/h5-bundle-03-vendor-update-live-probes-v0/validation.md`
- `examples/connectors/h5_vendor_update_driver/live_probe_results/`
- `examples/connectors/h5_vendor_update_driver/live_probe_outputs/`

## NON_GOALS

- No new live calls, API calls, provider/model calls, browser automation,
  catalog fetching or sync, downloads, installs, execution, scraping, crawling,
  vendor tool invocation, package manager invocation, firmware flashing, source
  sync, public query fanout, public/master index mutation, evidence acceptance,
  candidate acceptance, source truth acceptance, identity truth acceptance,
  compatibility truth acceptance, authenticity truth acceptance, safety truth
  acceptance, public truth creation, public launch, deployment, or
  production-readiness claims.

## OUTPUT_SCHEMA

Future H5-BUNDLE-04 responses should preserve status, summary, commits,
H5 exit/next-phase decisions, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1450
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
