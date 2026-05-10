# AIDE Latest Task Packet

## PHASE

H3-BUNDLE-02 - OS package archive fixture runtimes and normalizers

## GOAL

Prepare the next Eureka H3 task after H3-BUNDLE-01. This packet is a compact AIDE resumption handoff only; it does not itself authorize code edits or Eureka product behavior changes. A future task prompt must explicitly scope H3-BUNDLE-02 implementation before product paths are edited.

H3-BUNDLE-02 should add committed-fixture-only OS package archive fixture replay and normalizer runtime after H3 policy packs close.

## WHY

H3-BUNDLE-01 adds OS package archive source-family policy packs for thirteen sources with source records, connector-family assignments, identity and platform compatibility policies, approval gates, coverage previews, scorecard previews, docs, scripts, tests, and audit evidence. H3 remains policy-pack-only: no live access, no repository index fetch, no package downloads, no package-manager invocation, no install or execution, no source sync, no public/master index mutation, and no truth acceptance.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/H3-BUNDLE-01/task.yaml`
- `.aide/queue/H3-BUNDLE-02/task.yaml`
- `HUMAN-OBS-REVIEW-01` parallel side-lane remains preserved for human observation review.
- `control/audits/h3-bundle-01-os-package-archive-policy-packs-v0/`
- `control/audits/h2-bundle-04-package-review-quality-audit-v0/`
- `control/inventory/source_packs/h3_os_package_archive_sources.json`
- `control/inventory/source_packs/h3_os_package_archive_source_pack_policy.json`
- `scripts/validate_h3_os_package_archive_policy_packs.py`
- `scripts/summarize_h3_os_package_archive_sources.py`
- `scripts/check_architecture_boundaries.py`

## ALLOWED_PATHS

- `.aide/**`
- H3 fixture-runtime paths only if a future prompt explicitly scopes H3-BUNDLE-02 implementation.

## IMPLEMENTATION

- Do not start H3-BUNDLE-02 implementation from this packet alone.
- Resume from repo-local evidence, especially `.aide/queue/` and `control/audits/h3-bundle-01-os-package-archive-policy-packs-v0/`.
- Treat H3 source records, policy packs, coverage previews, and scorecard previews as planning artifacts only.
- Preserve no-live-call, no-repository-index-fetch, no-download, no-package-manager-invocation, no-install, no-execute, no-source-sync, no-index-mutation, and no-truth-acceptance boundaries.
- H3 fixture work must use committed synthetic or public-safe fixtures only and must not infer OS package identity truth, compatibility correctness, dependency correctness, installability, rights clearance, malware safety, or production coverage.
- No Eureka product behavior change is authorized by this handoff.

## ACCEPTANCE

- Latest handoff points to H3-BUNDLE-02.
- H3-BUNDLE-01 evidence remains reviewable.
- H3 policy packs validate offline.
- AIDE doctor, validate, test, selftest, eval run, and verify are available as local validation lanes.
- No live source calls, repository index fetches, package downloads, package-manager invocation, installs, execution, scraping, crawling, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, package identity truth acceptance, compatibility truth acceptance, or product behavior changes are authorized by this handoff.

## VALIDATION

- `python scripts/validate_h3_os_package_archive_policy_packs.py`
- `python scripts/summarize_h3_os_package_archive_sources.py --check`
- `python -m unittest tests.operations.test_h3_os_package_archive_policy_packs`
- `python -m unittest tests.operations.test_h3_os_package_archive_summary`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- `.aide/queue/index.yaml`
- `.aide/queue/H3-BUNDLE-01/task.yaml`
- `.aide/queue/H3-BUNDLE-02/task.yaml`
- `HUMAN-OBS-REVIEW-01` parallel side-lane remains preserved for human observation review.
- `control/audits/h3-bundle-01-os-package-archive-policy-packs-v0/h3_bundle_01_report.json`
- `control/audits/h3-bundle-01-os-package-archive-policy-packs-v0/validation.md`
- `control/audits/h3-bundle-01-os-package-archive-policy-packs-v0/h3_readiness_for_fixture_runtime.md`

## NON_GOALS

- Do not rely on full chat history or pasted whole-repository contents.
- No downloads, installs, execution, scraping, crawling, repository index fetches, repository mirrors, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, package identity truth acceptance, compatibility truth acceptance, dependency correctness acceptance, public truth creation, public launch, deployment, or production-readiness claims.
- No live probe execution without explicit committed source approval.

## OUTPUT_SCHEMA

Future H3-BUNDLE-02 responses should preserve status, summary, commits, changed paths, validation, H3 fixture-only scope, no-download boundary, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1250
- budget_status: within_budget

## FORBIDDEN_PATHS

- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `native/**`
- `crates/**`
- `connectors/**`
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
