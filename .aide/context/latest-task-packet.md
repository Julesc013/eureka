# AIDE Latest Task Packet

## PHASE

H2-BUNDLE-03 - Package registry approved metadata-only live probes

## GOAL

Prepare the next Eureka H2 task after H2-BUNDLE-02 package-registry fixture
runtimes and normalizers. H2-BUNDLE-03 should add approval-gated, fail-closed
metadata-only live-probe envelopes and blocked-by-default scripts for the H2
package registry sources.

This packet is a Eureka AIDE resumption handoff with no Eureka product behavior
change. A future task prompt must scope implementation before code changes
proceed.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## WHY

H2-BUNDLE-02 proves fixture parsing and candidate-only normalization for Maven
Central, NuGet, crates.io, RubyGems, CPAN, CRAN, conda-forge, and OCI registry
metadata. The next source-lane step is to define live-probe envelopes that are
explicitly blocked until committed source approval exists.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/H2-BUNDLE-02/task.yaml`
- `.aide/queue/H2-BUNDLE-03/task.yaml`
- `control/audits/h2-bundle-02-package-fixture-runtime-v0/`
- `runtime/connectors/h2_package_registries/`
- `examples/connectors/h2_package_registries/fixtures/`
- `examples/connectors/h2_package_registries/normalized/`
- `examples/connectors/h2_package_registries/replay_results/`
- `scripts/validate_h2_package_registry_fixture_runtime.py`
- `scripts/validate_h2_package_registry_policy_packs.py`

## ALLOWED_PATHS

- `.aide/**`
- local-only planning docs or audit notes under `control/audits/**` if a future
  prompt explicitly scopes them.

## IMPLEMENTATION

- Keep all H2 live-probe behavior fail-closed unless a committed approval
  artifact explicitly allows one metadata-only request.
- Reuse H0/H1 live-probe envelope and kill-switch patterns.
- Preserve package-download, install, execute, source-sync, index-mutation, and
  truth-acceptance prohibitions.
- Treat fixture outputs from H2-BUNDLE-02 as replay evidence only.

## ACCEPTANCE

- H2-BUNDLE-03 artifacts validate offline.
- Live probes remain blocked by default.
- No package downloads, source archive downloads, OCI layer pulls,
  package-manager invocations, installs, execution, public/master index
  mutations, or truth acceptance occur.

## VALIDATION

- `python scripts/validate_h2_package_registry_fixture_runtime.py`
- `python scripts/replay_h2_package_fixtures.py --check`
- `python scripts/validate_h2_package_registry_policy_packs.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- `control/audits/h2-bundle-02-package-fixture-runtime-v0/h2_bundle_02_report.json`
- `control/audits/h2-bundle-02-package-fixture-runtime-v0/fixture_runtime_summary.md`
- `control/audits/h2-bundle-02-package-fixture-runtime-v0/no_live_call_report.md`
- `control/audits/h2-bundle-02-package-fixture-runtime-v0/no_download_report.md`
- `control/audits/h2-bundle-02-package-fixture-runtime-v0/validation.md`

## NON_GOALS

- No deployment, hosting, provider API calls, DNS changes, or public alpha launch
  claims.
- No live source calls unless a future task includes explicit committed source
  approval.
- No package downloads, artifact downloads, source archive downloads, OCI
  manifest/layer pulls, package-manager invocations, installs, execution,
  scraping, crawling, or browser automation.
- No public search behavior change, source sync, public query fanout,
  public-index mutation, master-index mutation, evidence acceptance, candidate
  acceptance, source truth acceptance, or public truth creation.
- No rights-clearance, malware-safety, verified-installability,
  dependency-correctness, or production-readiness claims.

## OUTPUT_SCHEMA

Future H2 responses should preserve status, summary, commits, changed paths,
validation, H2 live-probe scope, no-download boundary, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1300
- budget_status: within_budget

## FORBIDDEN_PATHS

- `site/dist/**`
- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`
