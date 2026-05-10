# AIDE Latest Task Packet

## PHASE

MVP-ALPHA-OPERATOR-REVIEW-01 - Operator review and launch decision packet

## GOAL

Continue after MVP-ALPHA-AUDIT-01 by preparing the human/operator review and
launch decision packet. This is a review-gated step only. It must not deploy,
call providers, change DNS, enable public hosting, enable public relay, mutate
site/dist, mutate public or master indexes, enable unsafe behavior, infer
operator signoff, or claim public alpha is live. It must proceed without
changing Eureka product behavior.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## WHY

MVP-ALPHA-AUDIT-01 added local MVP readiness contracts, policies, examples,
scripts, tests, and audit evidence. The gate is READY_WITH_WARNINGS: the local
fixture and audit spine is coherent enough for operator review, while Track A
final audit naming, H1 approval-gated posture, native manual build evidence,
and missing public launch evidence remain documented warnings.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/MVP-ALPHA-AUDIT-01/task.yaml`
- `.aide/queue/MVP-ALPHA-OPERATOR-REVIEW-01/task.yaml`
- `control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/`
- `examples/audits/mvp_alpha/`
- `contracts/audits/`
- `docs/operations/MVP_ALPHA_OPERATOR_REVIEW.md`

## ALLOWED_PATHS

- `.aide/**`
- operator review docs/evidence under `control/audits/**` if a future prompt
  explicitly scopes them.

## IMPLEMENTATION

- This packet is for operator review without changing Eureka product behavior.
- Use MVP-ALPHA-AUDIT-01 evidence as read-only context.
- Require explicit human/operator decision before any future public launch
  evidence collection.
- Keep launch, provider, DNS, hosting, public relay, live source fanout,
  downloads, uploads, accounts, telemetry, public/master index mutation, and
  production claims disabled.

## ACCEPTANCE

- Operator review packet references MVP-ALPHA-AUDIT-01 evidence.
- Signoff is explicit, not inferred.
- Any decision to continue names the next reviewed task.
- Any warning or blocker is preserved honestly.

## VALIDATION

- `python scripts/validate_mvp_alpha_audit.py`
- `python scripts/audit_mvp_alpha_readiness.py --check`
- `python scripts/build_mvp_alpha_operator_review_packet.py --check`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/mvp_alpha_audit_01_report.json`
- `control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/mvp_alpha_gate_decision.md`
- `control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/operator_review_packet.md`
- `control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/remediation_plan.md`
- `control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/validation.md`

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
- No generated site output regeneration, local private-state roots,
  rights-clearance claims, malware-safety claims, verified installability
  claims, public alpha live claims, production claims, or inferred signoff.

## OUTPUT_SCHEMA

Future operator-review responses should preserve status, summary, commits,
changed paths, validation, decision/scope, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 980
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
