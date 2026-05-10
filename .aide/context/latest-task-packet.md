# AIDE Latest Task Packet

## PHASE

H3-BUNDLE-04 - OS package archive review integration and quality delta

## GOAL

Prepare the next Eureka H3 task after H3-BUNDLE-03. This packet is a compact AIDE resumption handoff only; it does not itself authorize code edits or Eureka product behavior changes. A future task prompt must explicitly scope H3-BUNDLE-04 implementation before product paths are edited.

H3-BUNDLE-04 should integrate H3 fixture replay outputs and H3 blocked live-probe reports into review previews, quality delta evidence, source-pack update previews, and the H3 wave closeout.

## WHY

H3-BUNDLE-03 adds fail-closed metadata-only live-probe envelopes for thirteen OS package archive sources. Current committed policies do not approve live access, so all example live probes are blocked before network and request_count remains 0.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `HUMAN-OBS-REVIEW-01` parallel side-lane remains preserved for human observation review.
- `.aide/queue/H3-BUNDLE-03/task.yaml`
- `.aide/queue/H3-BUNDLE-04/task.yaml`
- `control/audits/h3-bundle-03-os-package-live-probes-v0/`
- `control/audits/h3-bundle-02-os-package-fixture-runtime-v0/`
- `runtime/connectors/h3_os_package_archives/`
- `scripts/validate_h3_os_package_live_probe.py`
- `scripts/run_h3_os_package_live_probe.py`
- `scripts/summarize_h3_os_package_live_probe_outputs.py`
- `scripts/check_architecture_boundaries.py`

## ALLOWED_PATHS

- `.aide/**`
- H3 review/quality/audit paths only if a future prompt explicitly scopes H3-BUNDLE-04 implementation.

## IMPLEMENTATION

- Do not start H3-BUNDLE-04 implementation from this packet alone.
- Resume from repo-local evidence, especially `.aide/queue/` and `control/audits/h3-bundle-03-os-package-live-probes-v0/`.
- Preserve fail-closed live probe behavior unless committed source-specific approvals exist.
- Preserve no-repository-index-sync, no-download, no-package-manager-invocation, no-install, no-execute, no-source-sync, no-index-mutation, and no-truth-acceptance boundaries.
- No Eureka product behavior change is authorized by this handoff.

## ACCEPTANCE

- Latest handoff points to H3-BUNDLE-04.
- H3-BUNDLE-03 evidence remains reviewable.
- H3 live-probe framework validates offline.
- No live source calls, repository index sync, downloads, package-manager invocation, installs, execution, scraping, crawling, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, package identity truth acceptance, compatibility truth acceptance, dependency correctness acceptance, or product behavior changes are authorized by this handoff.

## VALIDATION

- `python scripts/validate_h3_os_package_live_probe.py`
- `python scripts/run_h3_os_package_live_probe.py --source-id debian_snapshot --request-key example_package_metadata --check`
- `python scripts/summarize_h3_os_package_live_probe_outputs.py --input examples/connectors/h3_os_package_archives/live_probe_results --check`
- `python -m unittest tests.connectors.test_h3_os_package_live_probe`
- `python -m unittest tests.operations.test_h3_os_package_live_probe_scripts`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- `.aide/queue/index.yaml`
- `.aide/queue/H3-BUNDLE-03/task.yaml`
- `.aide/queue/H3-BUNDLE-04/task.yaml`
- `control/audits/h3-bundle-03-os-package-live-probes-v0/h3_bundle_03_report.json`
- `control/audits/h3-bundle-03-os-package-live-probes-v0/validation.md`

## NON_GOALS

- Do not rely on full chat history or pasted whole-repository contents.
- No downloads, installs, execution, scraping, crawling, repository index sync, repository mirrors, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, package identity truth acceptance, compatibility truth acceptance, dependency correctness acceptance, public truth creation, public launch, deployment, or production-readiness claims.
- No live probe execution without explicit committed source approval.

## OUTPUT_SCHEMA

Future H3-BUNDLE-04 responses should preserve status, summary, commits, changed paths, validation, H3 review scope, no-download/no-index-sync boundary, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1350
- budget_status: within_budget

## FORBIDDEN_PATHS

- `surfaces/**`
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
- repository mirror roots
