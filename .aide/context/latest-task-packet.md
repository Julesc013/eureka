# AIDE Latest Task Packet

## PHASE

H4-BUNDLE-01 - Code/source/release host source-family policy packs

## GOAL

Prepare the next Eureka H4 task after H3-BUNDLE-04. This packet is a compact AIDE resumption handoff only; it does not itself authorize code edits or product behavior changes. A future task prompt must explicitly scope H4-BUNDLE-01 implementation before product paths are edited.

H4-BUNDLE-01 should add code/source/release host source-family policy packs using H3 fixture-equivalent review outputs as precedent.

## WHY

H3-BUNDLE-04 closes OS package archive review integration with PASS_WITH_WARNINGS because H3 live probes are blocked by missing committed operator approval but fixture-equivalent outputs are sufficient for H4 policy planning.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `HUMAN-OBS-REVIEW-01` parallel side-lane remains preserved for human observation review.
- `.aide/queue/H3-BUNDLE-04/task.yaml`
- `.aide/queue/H4-BUNDLE-01/task.yaml`
- `control/audits/h3-bundle-04-os-package-review-quality-audit-v0/`
- `runtime/connectors/h3_os_package_archives/review_integration.py`
- `scripts/validate_h3_os_package_review_quality_audit.py`
- `scripts/audit_h3_os_package_archive_wave.py`

## ALLOWED_PATHS

- `.aide/**`
- H4 policy-pack paths only if a future prompt explicitly scopes H4-BUNDLE-01 implementation.

## IMPLEMENTATION

- Do not start H4-BUNDLE-01 implementation from this packet alone.
- Resume from repo-local evidence, especially `.aide/queue/` and `control/audits/h3-bundle-04-os-package-review-quality-audit-v0/`.
- Preserve no-live-call, no-repository-index-sync, no-download, no-package-manager-invocation, no-install, no-execute, no-source-sync, no-index-mutation, and no-truth-acceptance boundaries.
- No Eureka product behavior change is authorized by this handoff.

## ACCEPTANCE

- Latest handoff points to H4-BUNDLE-01.
- H3-BUNDLE-04 evidence remains reviewable.
- No live source calls, repository index sync, downloads, package-manager invocation, installs, execution, source sync, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, package identity truth acceptance, compatibility truth acceptance, dependency correctness acceptance, or product behavior changes are authorized by this handoff.

## VALIDATION

- `python scripts/validate_h3_os_package_review_quality_audit.py`
- `python scripts/audit_h3_os_package_archive_wave.py --check`
- `python -m unittest tests.connectors.test_h3_os_package_review_integration_quality`
- `python -m unittest tests.operations.test_h3_os_package_review_quality_scripts`
- `python -m unittest tests.operations.test_h3_os_package_integration_audit`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- `.aide/queue/index.yaml`
- `.aide/queue/H3-BUNDLE-04/task.yaml`
- `.aide/queue/H4-BUNDLE-01/task.yaml`
- `control/audits/h3-bundle-04-os-package-review-quality-audit-v0/h3_bundle_04_report.json`
- `control/audits/h3-bundle-04-os-package-review-quality-audit-v0/validation.md`

## NON_GOALS

- No downloads, installs, execution, scraping, crawling, repository index sync, repository mirrors, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, package identity truth acceptance, compatibility truth acceptance, dependency correctness acceptance, public truth creation, public launch, deployment, or production-readiness claims.

## OUTPUT_SCHEMA

Future H4-BUNDLE-01 responses should preserve status, summary, commits, changed paths, validation, source-family policy scope, no-live/no-download boundaries, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 900
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
- repository mirror roots
