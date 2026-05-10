# AIDE Latest Task Packet

## PHASE

H3-BUNDLE-03 - OS package archive approved metadata-only live probes

## GOAL

Prepare the next Eureka H3 task after H3-BUNDLE-02. This packet is a compact AIDE resumption handoff only; it does not itself authorize code edits or Eureka product behavior changes. A future task prompt must explicitly scope H3-BUNDLE-03 implementation before product paths are edited.

H3-BUNDLE-03 should add fail-closed, approval-gated, metadata-only live probe envelopes for OS package archives after the fixture runtime closes.

## WHY

H3-BUNDLE-02 adds fixture-only OS package archive normalizers and replay outputs for thirteen sources. H3 fixture outputs remain candidate-only: no live access, no source sync, no repository index fetch, no package downloads, no package-manager invocation, no install or execution, no public/master index mutation, and no package identity, compatibility, dependency, source, evidence, candidate, or public truth acceptance.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/H3-BUNDLE-02/task.yaml`
- `.aide/queue/H3-BUNDLE-03/task.yaml`
- `HUMAN-OBS-REVIEW-01` parallel side-lane remains preserved for human observation review.
- `control/audits/h3-bundle-02-os-package-fixture-runtime-v0/`
- `control/audits/h3-bundle-01-os-package-archive-policy-packs-v0/`
- `runtime/connectors/h3_os_package_archives/`
- `scripts/validate_h3_os_package_archive_fixture_runtime.py`
- `scripts/replay_h3_os_package_fixtures.py`
- `scripts/check_architecture_boundaries.py`

## ALLOWED_PATHS

- `.aide/**`
- H3 live-probe paths only if a future prompt explicitly scopes H3-BUNDLE-03 implementation.

## IMPLEMENTATION

- Do not start H3-BUNDLE-03 implementation from this packet alone.
- Resume from repo-local evidence, especially `.aide/queue/` and `control/audits/h3-bundle-02-os-package-fixture-runtime-v0/`.
- Preserve fail-closed live probe behavior unless committed source-specific approvals exist.
- Preserve no-repository-index-fetch, no-download, no-package-manager-invocation, no-install, no-execute, no-source-sync, no-index-mutation, and no-truth-acceptance boundaries.
- No Eureka product behavior change is authorized by this handoff.

## ACCEPTANCE

- Latest handoff points to H3-BUNDLE-03.
- H3-BUNDLE-02 evidence remains reviewable.
- H3 fixture runtime validates offline.
- No live source calls, repository index fetches, package downloads, package-manager invocation, installs, execution, scraping, crawling, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, package identity truth acceptance, compatibility truth acceptance, dependency correctness acceptance, or product behavior changes are authorized by this handoff.

## VALIDATION

- `python scripts/validate_h3_os_package_archive_fixture_runtime.py`
- `python scripts/replay_h3_os_package_fixtures.py --check`
- `python scripts/summarize_h3_os_package_fixture_outputs.py --input examples/connectors/h3_os_package_archives --check`
- `python -m unittest tests.connectors.test_h3_os_package_fixture_runtime`
- `python -m unittest tests.operations.test_h3_os_package_fixture_scripts`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- `.aide/queue/index.yaml`
- `.aide/queue/H3-BUNDLE-02/task.yaml`
- `.aide/queue/H3-BUNDLE-03/task.yaml`
- `control/audits/h3-bundle-02-os-package-fixture-runtime-v0/h3_bundle_02_report.json`
- `control/audits/h3-bundle-02-os-package-fixture-runtime-v0/validation.md`

## NON_GOALS

- Do not rely on full chat history or pasted whole-repository contents.
- No downloads, installs, execution, scraping, crawling, repository index fetches, repository mirrors, source sync, public query fanout, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, package identity truth acceptance, compatibility truth acceptance, dependency correctness acceptance, public truth creation, public launch, deployment, or production-readiness claims.
- No live probe execution without explicit committed source approval.

## OUTPUT_SCHEMA

Future H3-BUNDLE-03 responses should preserve status, summary, commits, changed paths, validation, H3 metadata-only scope, no-download boundary, risks, and next task.

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
