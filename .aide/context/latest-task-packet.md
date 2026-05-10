# AIDE Latest Task Packet

## PHASE

H5-BUNDLE-02 - Vendor/update/driver fixture runtimes and normalizers

## GOAL

Prepare the next Eureka H5 task after H5-BUNDLE-01. This packet is a compact
AIDE resumption handoff only; it does not itself authorize live source calls,
catalog fetching, downloads, vendor tool invocation, package manager invocation,
installer execution, firmware flashing, source sync, public/master index
mutation, truth acceptance, or changing Eureka product behavior.

H5-BUNDLE-02 should add fixture-only runtimes, committed synthetic fixtures,
normalizers, replay reports, candidate previews, docs, tests, and audit evidence
for vendor/update/driver/firmware and runtime redistributable metadata if a
future prompt explicitly scopes that work.

## WHY

H5-BUNDLE-01 added policy-pack-only source-family structure for fifteen H5
vendor/update/driver/firmware sources. The H5 policy wave remains offline and
blocked from live access, catalog fetches, downloads, installers, vendor tools,
package managers, firmware flashing, index mutation, and truth acceptance.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/H5-BUNDLE-01/task.yaml`
- `.aide/queue/H5-BUNDLE-02/task.yaml`
- `control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/`
- `control/inventory/source_packs/h5_vendor_update_driver_source_pack_policy.json`
- `control/inventory/source_packs/h5_vendor_update_driver_sources.json`
- `control/inventory/source_packs/h5_vendor_update_driver_connector_families.json`
- `control/inventory/source_packs/h5_vendor_identity_policy.json`
- `control/inventory/source_packs/h5_driver_device_compatibility_policy.json`
- `control/inventory/source_packs/h5_firmware_update_policy.json`
- `control/inventory/source_packs/h5_runtime_redistributable_policy.json`
- `examples/connectors/h5_vendor_update_driver/`
- `examples/source_packs/h5_vendor_update_driver_source_pack_manifest_v0.json`
- `docs/operations/H5_VENDOR_UPDATE_DRIVER_FIXTURE_PLAN.md`

## ALLOWED_PATHS

- `.aide/**`
- H5 fixture-runtime paths only if a future prompt explicitly scopes
  H5-BUNDLE-02 implementation.

## IMPLEMENTATION

- Do not start H5-BUNDLE-02 implementation from this packet alone.
- Resume from repo-local evidence, especially H5-BUNDLE-01 audit outputs.
- Preserve no-live-call, no-catalog-fetch, no-download, no-install,
  no-execute, no-firmware-flash, no-source-sync, no-index-mutation, and
  no-truth-acceptance boundaries.
- Treat vendor identity, driver identity, firmware/update identity, runtime
  identity, device compatibility, hash/signature metadata, source-cache,
  evidence, and review outputs as candidates/previews only until future
  reviewed gates explicitly accept them.

## ACCEPTANCE

- Latest handoff points to H5-BUNDLE-02.
- H5-BUNDLE-01 evidence remains reviewable.
- No Eureka product behavior change is authorized by this handoff.
- No live source calls, catalog fetches, downloads, driver downloads, firmware
  downloads, runtime downloads, installer downloads, update package downloads,
  checksum/signature downloads, vendor tool invocation, package manager
  invocation, firmware flashing, installs, execution, source sync, public/master
  index mutation, evidence acceptance, candidate acceptance, source truth
  acceptance, vendor/driver/firmware/runtime identity truth acceptance,
  compatibility truth acceptance, authenticity truth acceptance, safety truth
  acceptance, rights clearance, malware safety, installability, hosting,
  deployment, or product behavior changes are authorized by this handoff.

## VALIDATION

- `python scripts/validate_h5_vendor_update_driver_policy_packs.py`
- `python scripts/summarize_h5_vendor_update_driver_sources.py --check`
- `python -m unittest tests.operations.test_h5_vendor_update_driver_policy_packs`
- `python -m unittest tests.operations.test_h5_vendor_update_driver_summary`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- `.aide/queue/index.yaml`
- `.aide/queue/H5-BUNDLE-01/task.yaml`
- `.aide/queue/H5-BUNDLE-02/task.yaml`
- `control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/h5_bundle_01_report.json`
- `control/audits/h5-bundle-01-vendor-update-driver-policy-packs-v0/validation.md`
- `examples/connectors/h5_vendor_update_driver/policies/`
- `examples/connectors/h5_vendor_update_driver/coverage/`
- `examples/connectors/h5_vendor_update_driver/scorecards/`

## NON_GOALS

- No live calls, API calls, provider/model calls, browser automation, catalog
  fetching, downloads, installs, execution, scraping, crawling, vendor tool
  invocation, package manager invocation, firmware flashing, source sync, public
  query fanout, public/master index mutation, evidence acceptance, candidate
  acceptance, source truth acceptance, identity truth acceptance, compatibility
  truth acceptance, authenticity truth acceptance, safety truth acceptance,
  public truth creation, public launch, deployment, or production-readiness
  claims.

## OUTPUT_SCHEMA

Future H5-BUNDLE-02 responses should preserve status, summary, commits, H5
fixture scope boundaries, changed paths, validation, risks, and next task.

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
