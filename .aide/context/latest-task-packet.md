# AIDE Latest Task Packet

## PHASE

H5-BUNDLE-01 - Vendor, update, driver, and firmware source-family policy packs

## GOAL

Prepare the next Eureka H5 task after H4-BUNDLE-04. This packet is a compact
AIDE resumption handoff only; it does not itself authorize live source calls,
downloads, firmware or driver handling, installs, execution, source sync, public
or master index mutation, truth acceptance, or changing Eureka product behavior.

H5-BUNDLE-01 should add policy-pack-only source-family structure for vendor,
update, driver, and firmware metadata sources if a future prompt explicitly
scopes that work. No Eureka product behavior change is authorized by this
handoff.

## WHY

H4-BUNDLE-04 closed the code/source/release host wave with fixture-equivalent
review integration, quality delta, connector postmortem, and H5 readiness
evidence. H4 live probes remain blocked by missing operator approval, but
committed fixture replay outputs are sufficient for the next policy-pack-only
expansion lane.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `HUMAN-OBS-REVIEW-01` parallel side-lane remains preserved for human observation review.
- `.aide/queue/H4-BUNDLE-04/task.yaml`
- `.aide/queue/H5-BUNDLE-01/task.yaml`
- `control/audits/h4-bundle-04-code-source-review-quality-audit-v0/`
- `control/audits/h4-bundle-03-code-source-live-probes-v0/`
- `control/audits/h4-bundle-02-code-source-fixture-runtime-v0/`
- `control/audits/h4-bundle-01-code-source-release-policy-packs-v0/`
- `runtime/connectors/h4_code_source_release/`
- `examples/connectors/h4_code_source_release/review_integration/`

## ALLOWED_PATHS

- `.aide/**`
- H5 policy-pack paths only if a future prompt explicitly scopes H5-BUNDLE-01 implementation.

## IMPLEMENTATION

- Do not start H5-BUNDLE-01 implementation from this packet alone.
- Resume from repo-local evidence, especially H4-BUNDLE-04 audit outputs.
- Preserve no-live-call, no-download, no-driver-or-firmware-handling,
  no-install, no-execute, no-source-sync, no-index-mutation, and
  no-truth-acceptance boundaries.
- Treat vendor/update/driver/firmware source records, capabilities, source
  identities, release/update identifiers, hardware or platform compatibility,
  firmware/driver metadata, source-cache, evidence, and review outputs as
  candidates/previews only until future reviewed gates explicitly accept them.

## ACCEPTANCE

- Latest handoff points to H5-BUNDLE-01.
- H4-BUNDLE-04 evidence remains reviewable.
- No Eureka product behavior change is authorized by this handoff.
- No live source calls, downloads, firmware downloads, driver downloads,
  installer downloads, package downloads, source sync, public/master index
  mutation, evidence acceptance, candidate acceptance, source truth acceptance,
  identity truth acceptance, compatibility truth acceptance, provenance
  acceptance, authenticity acceptance, rights clearance, malware safety,
  installability, execution, hosting, deployment, or product behavior changes
  are authorized by this handoff.

## VALIDATION

- `python scripts/validate_h4_code_source_review_quality_audit.py`
- `python scripts/integrate_h4_code_source_review.py --input-dir examples/connectors/h4_code_source_release/replay_results --check`
- `python scripts/summarize_h4_code_source_quality_delta.py --input-dir examples/connectors/h4_code_source_release/review_integration --check`
- `python scripts/audit_h4_code_source_release_wave.py --check`
- `python -m unittest tests.connectors.test_h4_code_source_review_integration_quality`
- `python -m unittest tests.operations.test_h4_code_source_review_quality_scripts`
- `python -m unittest tests.operations.test_h4_code_source_integration_audit`
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
- `.aide/queue/H4-BUNDLE-04/task.yaml`
- `.aide/queue/H5-BUNDLE-01/task.yaml`
- `control/audits/h4-bundle-04-code-source-review-quality-audit-v0/h4_bundle_04_report.json`
- `control/audits/h4-bundle-04-code-source-review-quality-audit-v0/validation.md`
- `examples/connectors/h4_code_source_release/review_integration/`

## NON_GOALS

- No live calls, API calls, provider/model calls, browser automation, downloads,
  installs, execution, scraping, crawling, repository clones, git fetch, git
  command invocation, build tool invocation, firmware downloads, driver
  downloads, installer downloads, package downloads, source sync, public query
  fanout, public/master index mutation, evidence acceptance, candidate
  acceptance, source truth acceptance, identity truth acceptance, compatibility
  truth acceptance, provenance acceptance, authenticity acceptance, public truth
  creation, public launch, deployment, or production-readiness claims.

## OUTPUT_SCHEMA

Future H5-BUNDLE-01 responses should preserve status, summary, commits, H5
scope boundaries, changed paths, validation, risks, and next task.

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
- repository clone roots
- repository mirror roots
