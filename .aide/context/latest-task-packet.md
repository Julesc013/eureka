# AIDE Latest Task Packet

## PHASE

H4-BUNDLE-04 - Code/source/release host review integration and quality delta

## GOAL

Prepare the next Eureka H4 task after H4-BUNDLE-03. This packet is a compact
AIDE resumption handoff only; it does not itself authorize new live source
calls, repository clones, downloads, git/build commands, source sync, public or
master index mutation, truth acceptance, or changing Eureka product behavior.

H4-BUNDLE-04 should integrate H4 fixture-equivalent outputs and H4-BUNDLE-03
blocked live-probe reports into review seed previews, quality delta, connector
wave postmortem, integration audit, and next-phase recommendations without
changing Eureka product behavior.

## WHY

H4-BUNDLE-03 adds the fail-closed metadata-only live-probe framework for ten
code/source/release host sources. No source is currently approved for live
access; all live-probe examples are blocked offline with request_count 0 and
network_used false. H4-BUNDLE-02 fixture replay outputs are sufficient
fixture-equivalent material for review integration rehearsal.

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
- `.aide/queue/H4-BUNDLE-04/task.yaml`
- `control/audits/h4-bundle-03-code-source-live-probes-v0/`
- `control/audits/h4-bundle-02-code-source-fixture-runtime-v0/`
- `control/audits/h4-bundle-01-code-source-release-policy-packs-v0/`
- `runtime/connectors/h4_code_source_release/`
- `examples/connectors/h4_code_source_release/fixtures/`
- `examples/connectors/h4_code_source_release/normalized/`
- `examples/connectors/h4_code_source_release/replay_results/`
- `examples/connectors/h4_code_source_release/live_probe_results/`
- `examples/connectors/h4_code_source_release/live_probe_outputs/`

## ALLOWED_PATHS

- `.aide/**`
- H4 review integration paths only if a future prompt explicitly scopes
  H4-BUNDLE-04 implementation.

## IMPLEMENTATION

- Do not start H4-BUNDLE-04 implementation from this packet alone.
- Resume from repo-local evidence, especially H4-BUNDLE-02 fixture outputs and
  H4-BUNDLE-03 blocked live-probe reports.
- Preserve no-live-call, no-repository-clone, no-source-archive-download,
  no-release-asset-download, no-git-command, no-build-command, no-install,
  no-execute, no-source-sync, no-index-mutation, and no-truth-acceptance
  boundaries.
- Treat source identity, release identity, source-to-binary relation, release
  asset, source-cache, evidence, and review outputs as candidates/previews only.

## ACCEPTANCE

- Latest handoff points to H4-BUNDLE-04.
- H4-BUNDLE-03 evidence remains reviewable.
- No Eureka product behavior change is authorized by this handoff.
- No live source calls, repository clone, source archive downloads, release
  asset downloads, git command invocation, build tool invocation, installs,
  execution, source sync, public/master index mutation, evidence acceptance,
  candidate acceptance, source truth acceptance, source identity truth
  acceptance, release identity truth acceptance, source-to-binary relation truth
  acceptance, provenance acceptance, or product behavior changes are authorized
  by this handoff.

## VALIDATION

- `python scripts/validate_h4_code_source_live_probe.py`
- `python scripts/run_h4_code_source_live_probe.py --source-id github_releases --request-key example_release_metadata --check`
- `python scripts/summarize_h4_code_source_live_probe_outputs.py --input examples/connectors/h4_code_source_release/live_probe_results --check`
- `python scripts/validate_h4_code_source_release_fixture_runtime.py`
- `python scripts/validate_h4_code_source_release_policy_packs.py`
- `python -m unittest tests.connectors.test_h4_code_source_live_probe`
- `python -m unittest tests.operations.test_h4_code_source_live_probe_scripts`
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
- `.aide/queue/H4-BUNDLE-03/task.yaml`
- `.aide/queue/H4-BUNDLE-04/task.yaml`
- `control/audits/h4-bundle-03-code-source-live-probes-v0/h4_bundle_03_report.json`
- `control/audits/h4-bundle-03-code-source-live-probes-v0/validation.md`

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

Future H4-BUNDLE-04 responses should preserve status, summary, commits, H4 exit
decision, next-phase recommendation, changed paths, validation, scope
boundaries, risks, and next task.

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
- repository clone roots
- repository mirror roots
