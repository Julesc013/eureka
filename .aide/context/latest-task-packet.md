# AIDE Latest Task Packet

## PHASE

E-BUNDLE-02 - Hosted wrapper rehearsal and public launch evidence

## GOAL

Continue after E-BUNDLE-01 by preparing the next reviewed Eureka E-lane task:
hosted wrapper rehearsal and public launch evidence.

This handoff does not deploy anything. E-BUNDLE-02 must remain review-gated and
must not make provider changes, create provider credentials, configure DNS,
regenerate generated site output, enable a hosted backend, enable public relay,
call live sources, download files, install artifacts, execute artifacts, enable
uploads, accounts, telemetry, public index mutation, master index mutation, or
source/evidence/candidate/public truth acceptance by default.

This packet is a handoff only and proceeds with no Eureka product behavior
change.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## WHY

E-BUNDLE-01 defined hosting and operations readiness gates, public alpha
non-claims, host profiles, runtime config boundaries, rate limits, secrets,
observability, incident response, rollback, takedown, connector kill switches,
and launch evidence requirements without deploying anything. E-BUNDLE-02 can
rehearse launch evidence collection only if it preserves those boundaries.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/E-BUNDLE-01/task.yaml`
- `.aide/queue/E-BUNDLE-02/task.yaml`
- `control/audits/e-bundle-01-hosting-ops-readiness-v0/`
- `control/audits/c-bundle-03-native-smoke-packaging-v0/`
- `contracts/hosting/`
- `control/inventory/hosting/`
- `examples/hosting/`
- `docs/architecture/HOSTING_OPERATIONS_MODEL.md`
- `docs/architecture/PUBLIC_ALPHA_RUNTIME_BOUNDARY.md`
- `docs/operations/NO_DEPLOYMENT_IN_E_BUNDLE_01.md`

## ALLOWED_PATHS

- `.aide/**`
- Product path edits are to be defined by the E-BUNDLE-02 prompt.
- E-BUNDLE-01 artifacts are read-only context unless the next task explicitly
  scopes updates.

## IMPLEMENTATION

- Use E-BUNDLE-01 audit evidence as readiness context only.
- Keep hosted wrapper rehearsal separate from real deployment, provider state,
  DNS, credentials, public route activation, live source fanout, and production
  claims.
- Do not create hosted runtime state, deployment outputs, provider calls,
  credentials, telemetry, accounts, uploads, or public search behavior changes.

## ACCEPTANCE

- E-BUNDLE-02 acceptance criteria will be defined by its task prompt.
- This handoff is acceptable only if E-BUNDLE-01 validation remains PASS and no
  deployment, hosted behavior, provider change, DNS change, generated site
  output mutation, public relay, live access, public/master index mutation,
  truth acceptance, product behavior change, public alpha live claim, or
  production claim is introduced.

## VALIDATION

- `python scripts/validate_hosting_readiness.py`
- `python scripts/check_public_alpha_non_claims.py`
- `python scripts/check_hosting_boundaries.py`
- `python scripts/summarize_hosting_readiness.py --input examples/hosting --check`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/e-bundle-01-hosting-ops-readiness-v0/`
- `control/audits/e-bundle-01-hosting-ops-readiness-v0/e_bundle_01_report.json`
- `control/audits/e-bundle-01-hosting-ops-readiness-v0/validation.md`
- `control/audits/e-bundle-01-hosting-ops-readiness-v0/no_deployment_report.md`
- `control/audits/e-bundle-01-hosting-ops-readiness-v0/e_bundle_02_readiness_recommendation.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.md`

## NON_GOALS

- No deployment or hosting enablement.
- No provider API calls, provider credentials, secrets, DNS changes, or custom
  domain claims.
- No public relay or public bind.
- No live source calls, external/API/model/provider calls, or source sync.
- No downloads, mirroring, installs, execution, or emulation.
- No uploads, accounts, telemetry, or credential collection.
- No public search behavior change.
- No public index or master index mutation.
- No source, evidence, candidate, pack, action, snapshot, relay, native fixture,
  or public truth acceptance.
- No release binaries, build-output commits, generated site output regeneration,
  local private-state roots, rights-clearance claims, malware-safety claims,
  verified installability claims, public alpha live claims, or production
  claims.

## OUTPUT_SCHEMA

Future E-BUNDLE-02 task responses should preserve the repo task final schema:
status, summary, commits, changed paths, validation, hosting/ops scope,
readiness, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1260
- budget_status: within_budget

## FORBIDDEN_PATHS

- `contracts/**`
- `runtime/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `connectors/**`
- `packaging/**`
- `third_party/**`
- generated site distribution output
- `data/public_index/**`
- `data/master_index/**`
- `master_index/**`
- `.aide.local/**`
- `.local/eureka/**`
- `.cache/eureka/**`
