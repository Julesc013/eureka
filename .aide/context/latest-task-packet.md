# AIDE Latest Task Packet

## PHASE

H4-BUNDLE-03 - Code/source/release host approved metadata-only live probes

## GOAL

Prepare the next Eureka H4 task after H4-BUNDLE-02. This packet is a compact
AIDE resumption handoff only; it does not itself authorize live-probe
implementation, source access, or product behavior changes. A future task
prompt must explicitly scope H4-BUNDLE-03 implementation before product paths
are edited.

H4-BUNDLE-03 should add approval-gated, fail-closed metadata-only live-probe
planning for code/source/release hosts. No live call may run unless a future
prompt and committed policy explicitly approve one exact bounded metadata
request.

## WHY

H4-BUNDLE-02 adds fixture-only contracts, policies, runtime normalizers, scripts,
fixtures, normalized examples, replay results, source/release/relation/asset
candidate examples, tests, docs, and audit evidence for ten code/source/release
host metadata sources. The next bounded step is live-probe envelope planning,
with default offline preflight and blocked output if approval is missing.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `HUMAN-OBS-REVIEW-01` parallel side-lane remains preserved for human observation review.
- `.aide/queue/H4-BUNDLE-02/task.yaml`
- `.aide/queue/H4-BUNDLE-03/task.yaml`
- `control/audits/h4-bundle-02-code-source-fixture-runtime-v0/`
- `control/audits/h4-bundle-01-code-source-release-policy-packs-v0/`
- `runtime/connectors/h4_code_source_release/`
- `examples/connectors/h4_code_source_release/fixtures/`
- `examples/connectors/h4_code_source_release/normalized/`
- `examples/connectors/h4_code_source_release/replay_results/`
- `scripts/validate_h4_code_source_release_fixture_runtime.py`
- `scripts/replay_h4_code_source_fixtures.py`
- `scripts/summarize_h4_code_source_fixture_outputs.py`

## ALLOWED_PATHS

- `.aide/**`
- H4 live-probe paths only if a future prompt explicitly scopes H4-BUNDLE-03 implementation.

## IMPLEMENTATION

- Do not start H4-BUNDLE-03 implementation from this packet alone.
- Resume from repo-local evidence, especially `.aide/queue/` and `control/audits/h4-bundle-02-code-source-fixture-runtime-v0/`.
- Preserve no-repository-clone, no-source-archive-download, no-release-asset-download, no-git-command, no-build-command, no-install, no-execute, no-source-sync, no-index-mutation, and no-truth-acceptance boundaries.
- H4 live probes must default to offline validation and dry preflight.
- A missing approval must emit blocked output, not perform a source call.
- No Eureka product behavior change is authorized by this handoff.

## ACCEPTANCE

- Latest handoff points to H4-BUNDLE-03.
- H4-BUNDLE-02 evidence remains reviewable.
- No live source calls, repository clone, source archive downloads, release asset downloads, git command invocation, build tool invocation, installs, execution, source sync, public/master index mutation, evidence acceptance, candidate acceptance, source truth acceptance, source identity truth acceptance, release identity truth acceptance, source-to-binary relation truth acceptance, or product behavior changes are authorized by this handoff.

## VALIDATION

- `python scripts/validate_h4_code_source_release_fixture_runtime.py`
- `python scripts/replay_h4_code_source_fixtures.py --check`
- `python scripts/summarize_h4_code_source_fixture_outputs.py --input examples/connectors/h4_code_source_release --check`
- `python scripts/validate_h4_code_source_release_policy_packs.py`
- `python -m unittest tests.connectors.test_h4_code_source_fixture_runtime`
- `python -m unittest tests.connectors.test_h4_source_identity_mapping`
- `python -m unittest tests.connectors.test_h4_release_identity_mapping`
- `python -m unittest tests.connectors.test_h4_source_to_binary_relation_mapping`
- `python -m unittest tests.operations.test_h4_code_source_fixture_scripts`
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
- `.aide/queue/H4-BUNDLE-02/task.yaml`
- `.aide/queue/H4-BUNDLE-03/task.yaml`
- `control/audits/h4-bundle-02-code-source-fixture-runtime-v0/h4_bundle_02_report.json`
- `control/audits/h4-bundle-02-code-source-fixture-runtime-v0/validation.md`

## NON_GOALS

- No live calls, API calls, provider/model calls, browser automation, downloads,
  installs, execution, scraping, crawling, repository clones, git fetch, git
  command invocation, build tool invocation, source archive downloads, release
  asset downloads, binary downloads, source sync, public query fanout,
  public/master index mutation, evidence acceptance, candidate acceptance,
  source truth acceptance, source identity truth acceptance, release identity
  truth acceptance, source-to-binary relation truth acceptance, provenance
  acceptance, public truth creation, public launch, deployment, or
  production-readiness claims.

## OUTPUT_SCHEMA

Future H4-BUNDLE-03 responses should preserve status, summary, commits, live
probe result scope, changed paths, validation, metadata-only boundaries, risks,
and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1100
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
