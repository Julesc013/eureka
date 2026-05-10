# AIDE Latest Task Packet

## PHASE

H2-BUNDLE-02 - Package registry fixture runtimes and normalizers

## GOAL

Prepare the next H2 task after H2-BUNDLE-01 package-registry policy packs.
H2-BUNDLE-02 should add committed-fixture-only fixture replay and normalizer
support for the package registry source family while preserving the H0/H1/H2
source-policy boundaries.

This packet is a Eureka AIDE resumption handoff with no Eureka product behavior
change. A future task prompt must scope implementation before code changes
proceed. The default boundary remains
local and fixture-only: no live registry calls, source sync, package downloads,
package-manager invocation, installs, execution, scraping, public search
behavior changes, public/master index mutation, source/evidence/candidate truth
acceptance, provider calls, hosting, deployment, rights-clearance claims,
malware-safety claims, verified-installability claims, or dependency-correctness
claims.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## WHY

H2-BUNDLE-01 added package registry source records, source-family policy packs,
approval gates, output/truth/no-live/no-download policies, coverage previews,
scorecard previews, and package identity candidate policy. The next local
expansion should exercise those policies against committed fixtures only.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/H2-BUNDLE-01/task.yaml`
- `.aide/queue/H2-BUNDLE-02/task.yaml`
- `control/audits/h2-bundle-01-package-registry-policy-packs-v0/`
- `control/audits/h1-bundle-04-review-quality-audit-v0/`
- `control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/`

## ALLOWED_PATHS

- `.aide/**`
- local-only planning docs or audit notes under `control/audits/**` if a future
  prompt explicitly scopes them.

## IMPLEMENTATION

- Reuse the H0/H1 connector fixture-replay pattern.
- Keep H2 fixture runtime committed-fixture-only.
- Normalize package registry fixture records as candidates, not truth.
- Preserve package identity candidate boundaries.
- Keep all downloads, installs, execution, source sync, live probes, and public
  index use disabled.
- Do not change Eureka product behavior from this AIDE handoff packet alone.

## ACCEPTANCE

- H2 fixture replay and normalizer behavior remains offline and fixture-only.
- Package registry examples validate without live source access.
- Public/master indexes and public search behavior remain unchanged.
- No source/evidence/candidate truth is accepted.

## VALIDATION

- `python scripts/validate_h2_package_registry_policy_packs.py`
- `python scripts/summarize_h2_package_registry_sources.py --check`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/h2-bundle-01-package-registry-policy-packs-v0/h2_bundle_01_report.json`
- `control/audits/h2-bundle-01-package-registry-policy-packs-v0/h2_source_pack_summary.md`
- `control/audits/h2-bundle-01-package-registry-policy-packs-v0/h2_fixture_plan.md`
- `control/audits/h2-bundle-01-package-registry-policy-packs-v0/validation.md`

## NON_GOALS

- No deployment or launch.
- No provider API calls, provider credentials, secrets, DNS changes, or custom
  domain claims.
- No public relay, public bind, live source calls, source sync, or public query
  fanout.
- No package downloads, artifact downloads, source archive downloads, OCI layer
  pulls, mirroring, installs, execution, emulation, or package-manager commands.
- No public search behavior change.
- No public index or master index mutation.
- No source, evidence, candidate, pack, action, snapshot, relay, native fixture,
  or public truth acceptance.
- No generated site output regeneration, local private-state roots,
  rights-clearance claims, malware-safety claims, verified-installability
  claims, dependency-correctness claims, public alpha live claims, production
  claims, or inferred signoff.

## OUTPUT_SCHEMA

Future H2 responses should preserve status, summary, commits, changed paths,
validation, H2 fixture scope, no-live/no-download boundary, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1200
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
