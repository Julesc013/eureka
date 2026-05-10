# AIDE Latest Task Packet

## PHASE

MVP-ALPHA-AUDIT-01 - End-to-end local MVP readiness audit

## GOAL

Continue after E-BUNDLE-02 by preparing the next reviewed Eureka lane:
an end-to-end local MVP alpha readiness audit.

This packet is a handoff only. MVP-ALPHA-AUDIT-01 must remain local,
fixture-oriented, review-gated, and non-deploying unless a future reviewed
prompt explicitly scopes otherwise, without changing Eureka product behavior.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## WHY

E-BUNDLE-02 added hosted-wrapper rehearsal contracts, local fixture smoke
matrix checks, blocked request reports, public alpha status reports, launch
evidence packet requirements, operator signoff requirements, post-launch
remediation planning, runtime helpers, scripts, tests, and audit evidence
without deploying anything.

The next useful step is a local MVP alpha audit that reads the accumulated
A/B/H/F/G/I/J0/D/C/E evidence and decides what is locally ready, what is
operator-gated, and what remains blocked before any public launch claim.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/E-BUNDLE-02/task.yaml`
- `.aide/queue/MVP-ALPHA-AUDIT-01/task.yaml`
- `control/audits/e-bundle-01-hosting-ops-readiness-v0/`
- `control/audits/e-bundle-02-hosted-wrapper-rehearsal-v0/`
- `control/audits/c-bundle-03-native-smoke-packaging-v0/`
- `contracts/hosting/`
- `runtime/hosting/`
- `examples/hosting/`
- `docs/operations/E_TRACK_COMPLETION_AUDIT.md`

## ALLOWED_PATHS

- `.aide/**`
- MVP alpha audit paths are to be defined by the next task prompt.
- E-BUNDLE-02 artifacts are read-only context unless the next task explicitly
  scopes updates.

## IMPLEMENTATION

- Use E-BUNDLE-02 audit evidence as readiness context only.
- Keep local MVP audit separate from real deployment, provider state, DNS,
  credentials, public route activation, live source fanout, public relay,
  uploads, accounts, telemetry, downloads, and production claims.
- Preserve C-BUNDLE-03 native evidence as context, not release evidence.

## ACCEPTANCE

- MVP-ALPHA-AUDIT-01 acceptance criteria will be defined by its task prompt.
- This handoff is acceptable only if E-BUNDLE-02 validation remains PASS and no
  deployment, hosted behavior, provider change, DNS change, generated site
  output mutation, public relay, live access, public/master index mutation,
  truth acceptance, public alpha live claim, or production claim is introduced.

## VALIDATION

- `python scripts/validate_hosted_wrapper_rehearsal.py`
- `python scripts/audit_public_alpha_readiness.py --check`
- `python scripts/check_public_alpha_blocked_requests.py --input examples/hosting/blocked_requests --check`
- `python scripts/check_public_launch_evidence.py --input examples/hosting/launch/public_launch_evidence_packet_required_v0.json --check`
- `python scripts/validate_hosting_readiness.py`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/e-bundle-02-hosted-wrapper-rehearsal-v0/e_bundle_02_report.json`
- `control/audits/e-bundle-02-hosted-wrapper-rehearsal-v0/validation.md`
- `control/audits/e-bundle-02-hosted-wrapper-rehearsal-v0/no_deployment_report.md`
- `control/audits/e-bundle-02-hosted-wrapper-rehearsal-v0/public_launch_readiness_audit.md`
- `control/audits/e-bundle-02-hosted-wrapper-rehearsal-v0/next_phase_recommendation.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.md`

## NON_GOALS

- No deployment or hosting enablement.
- No provider API calls, provider credentials, secrets, DNS changes, or custom
  domain claims.
- No public relay or public bind.
- No live source calls, external/API/model/provider calls, source sync, or
  public query fanout.
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

Future MVP-ALPHA-AUDIT-01 task responses should preserve the repo task final
schema: status, summary, commits, changed paths, validation, scope,
readiness, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1340
- budget_status: within_budget

## FORBIDDEN_PATHS

- generated site distribution output
- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `site/dist/**`
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
