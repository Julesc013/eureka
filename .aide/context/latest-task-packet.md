# AIDE Latest Task Packet

## PHASE

H5-BUNDLE-03 - Vendor/update/driver approved metadata-only live probes

## GOAL

Prepare the next Eureka H5 task after H5-BUNDLE-02. This packet is a compact
AIDE resumption handoff only; it does not itself authorize live source calls,
catalog fetching, downloads, vendor tool invocation, package manager invocation,
installer execution, firmware flashing, source sync, public/master index
mutation, truth acceptance, or changing Eureka product behavior.

H5-BUNDLE-03 should add fail-closed, approval-gated metadata-only live-probe
envelopes for vendor/update/driver/firmware/runtime metadata only if a future
prompt explicitly scopes that work and committed policies approve exact bounded
requests.

HUMAN-OBS-REVIEW-01 remains preserved as a parallel side-lane and is not
completed, promoted, or replaced by this H5 live-probe handoff.

## WHY

H5-BUNDLE-02 added fixture-only normalizers, replay outputs, candidate previews,
docs, tests, policies, and audit evidence for fifteen H5 vendor/update/driver
sources. The H5 fixture runtime remains offline and blocked from live access,
catalog fetches, downloads, installers, vendor tools, package managers, firmware
flashing, index mutation, and truth acceptance.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/H5-BUNDLE-02/task.yaml`
- `.aide/queue/H5-BUNDLE-03/task.yaml`
- `control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/`
- `contracts/connectors/h5_vendor_update_*.v0.json`
- `contracts/connectors/h5_*candidate.v0.json`
- `runtime/connectors/h5_vendor_update_driver/`
- `examples/connectors/h5_vendor_update_driver/`
- `docs/operations/H5_VENDOR_UPDATE_FIXTURE_*.md`

## ALLOWED_PATHS

- `.aide/**`
- H5 live-probe policy, contract, runtime wrapper, script, example, test, docs,
  and audit paths only if a future prompt explicitly scopes H5-BUNDLE-03.

## IMPLEMENTATION

- Do not start H5-BUNDLE-03 implementation from this packet alone.
- Resume from repo-local evidence, especially H5-BUNDLE-02 audit outputs.
- Preserve fail-closed default behavior for every source.
- Do not infer operator approval for any live metadata probe.
- Preserve no-catalog-fetch, no-download, no-install, no-execute,
  no-firmware-flash, no-source-sync, no-index-mutation, and
  no-truth-acceptance boundaries.
- Treat vendor identity, driver identity, firmware/update identity, runtime
  identity, device compatibility, payload/hash/signature metadata, source-cache,
  evidence, and review outputs as candidates/previews only until future reviewed
  gates explicitly accept them.

## ACCEPTANCE

- Latest handoff points to H5-BUNDLE-03.
- H5-BUNDLE-02 evidence remains reviewable.
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

- `python scripts/validate_h5_vendor_update_driver_fixture_runtime.py`
- `python scripts/normalize_h5_vendor_update_fixture.py --source-id nvidia_driver_downloads --input examples/connectors/h5_vendor_update_driver/fixtures/nvidia_driver_downloads/typical_record.json --check`
- `python scripts/replay_h5_vendor_update_fixtures.py --check`
- `python scripts/summarize_h5_vendor_update_fixture_outputs.py --input examples/connectors/h5_vendor_update_driver --check`
- H5 targeted unit tests
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`
- AIDE Lite: `.aide/scripts/aide_lite.py doctor`; `.aide/scripts/aide_lite.py validate`; `.aide/scripts/aide_lite.py test`; `.aide/scripts/aide_lite.py selftest`; `.aide/scripts/aide_lite.py eval run`; `.aide/scripts/aide_lite.py verify`; review-pack; adapter validate

## EVIDENCE

- `.aide/queue/index.yaml`
- `.aide/queue/H5-BUNDLE-02/task.yaml`
- `.aide/queue/H5-BUNDLE-03/task.yaml`
- `control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/h5_bundle_02_report.json`
- `control/audits/h5-bundle-02-vendor-update-fixture-runtime-v0/validation.md`
- `examples/connectors/h5_vendor_update_driver/{fixtures,normalized,replay_results,identity}/`

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

Future H5-BUNDLE-03 responses should preserve status, summary, commits, live
probe scope boundaries, changed paths, validation, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1500
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
