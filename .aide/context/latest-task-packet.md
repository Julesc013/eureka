# AIDE Latest Task Packet

## PHASE

LOCAL-MVP-ITERATION-01 - Continue local MVP improvements pending operator decision

## GOAL

Continue after MVP-ALPHA-OPERATOR-REVIEW-01 using only local, review-gated planning. This default safe route exists because the operator review packet is unsigned. It must proceed without changing Eureka product behavior and must not deploy, launch, call providers, change DNS, enable public hosting, enable public relay, mutate generated site output, mutate public or master indexes, enable unsafe behavior, infer operator signoff, or claim public alpha is live.

HUMAN-OBS-REVIEW-01 remains a parallel side-lane.

## WHY

MVP-ALPHA-OPERATOR-REVIEW-01 prepared the human decision packet, signoff template, blocker register, public claim review, and decision-to-next-task routing. It intentionally did not infer approval. The default next task is local iteration unless a future explicit operator artifact selects planning, remediation, block, or deferred paths.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/context-index.json`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/latest-review-packet.md`
- `.aide/queue/MVP-ALPHA-OPERATOR-REVIEW-01/task.yaml`
- `.aide/queue/LOCAL-MVP-ITERATION-01/task.yaml`
- `control/audits/mvp-alpha-operator-review-01-v0/`
- `control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/`
- `examples/audits/mvp_alpha_operator/`

## ALLOWED_PATHS

- `.aide/**`
- local-only planning docs or audit notes under `control/audits/**` if a future prompt explicitly scopes them.

## IMPLEMENTATION

- Treat the operator review packet as unsigned.
- Require explicit human/operator decision before deployment planning can advance beyond planning-only artifacts.
- Keep launch, provider, DNS, hosting, public relay, live source fanout, downloads, uploads, accounts, telemetry, public/master index mutation, and production claims disabled.
- Do not accept evidence, candidates, packs, sources, actions, or public truth.

## ACCEPTANCE

- Local iteration remains bounded by the unsigned operator review posture.
- Any future decision path names a reviewed task.
- Any warning or blocker is preserved honestly.

## VALIDATION

- `python scripts/validate_mvp_alpha_operator_review.py`
- `python scripts/check_mvp_alpha_operator_signoff.py --input examples/audits/mvp_alpha_operator/operator_signoff_packet_unsigned_v0.json --check`
- `python scripts/check_mvp_alpha_public_claims.py --input examples/audits/mvp_alpha_operator --check`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval run`

## EVIDENCE

- `control/audits/mvp-alpha-operator-review-01-v0/mvp_alpha_operator_review_01_report.json`
- `control/audits/mvp-alpha-operator-review-01-v0/operator_decision_packet.md`
- `control/audits/mvp-alpha-operator-review-01-v0/operator_signoff_template.md`
- `control/audits/mvp-alpha-operator-review-01-v0/recommended_next_task.md`
- `control/audits/mvp-alpha-operator-review-01-v0/validation.md`

## NON_GOALS

- No deployment or launch.
- No provider API calls, provider credentials, secrets, DNS changes, or custom domain claims.
- No public relay or public bind.
- No live source calls, external/API/model/provider calls, source sync, or public query fanout.
- No downloads, mirroring, installs, execution, or emulation.
- No uploads, accounts, telemetry, or credential collection.
- No public search behavior change.
- No public index or master index mutation.
- No source, evidence, candidate, pack, action, snapshot, relay, native fixture, or public truth acceptance.
- No generated site output regeneration, local private-state roots, rights-clearance claims, malware-safety claims, verified installability claims, public alpha live claims, production claims, or inferred signoff.

## OUTPUT_SCHEMA

Future local-iteration responses should preserve status, summary, commits, changed paths, validation, decision/scope, risks, and next task.

## TOKEN_ESTIMATE

- method: manual chars / 4 estimate
- approx_tokens: 1120
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
