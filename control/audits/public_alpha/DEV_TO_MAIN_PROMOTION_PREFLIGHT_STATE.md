# Dev To Main Promotion Preflight State

Task: `DEV-TO-MAIN-PROMOTION-READINESS-AND-SYNC-00`

Generated at: `2026-06-17T15:09:54Z`

## Branch State

- Current branch: `dev`
- HEAD: `f523e3eccafcf2ccf02493d93e9ebee5ebcb3f78`
- Worktree before promotion reports: clean
- `origin/dev`: `f523e3eccafcf2ccf02493d93e9ebee5ebcb3f78`
- `origin/main`: `339b61d14d01e923fd87931523d849e4f26cf2ec`
- `origin/main...origin/dev`: `0 131`
- Branches diverged: no
- Main-only commits: none
- Fast-forward safe: yes

## Dev-Only Commit Summary

`origin/dev` is ahead of `origin/main` by 131 commits. The stack includes:

- public docs front door, status navigation, and docs guardrails
- public-alpha ops posture, exposure plan, operator choice, and operator-input reports
- local-machine staging, public-alpha release checks, launch-gate closeout, and read-only public-alpha foundations
- local search, local Workbench, reviewed-record, snapshot, review, candidate, and source-family foundations
- validation, full-discovery handoffs/ingests, queue handoffs, and generated-artifact repairs

Recent dev-only commits:

```text
f523e3ec docs(public-alpha): record tunnel operator input state
4d882a8a docs(public-alpha): record remote sync audit
b09498b7 test(docs): guard public docs links
1f4d0579 docs(index): add public documentation navigation
83c44fa6 docs(readme): create public project front door
910907f6 feat(operations): record public tunnel operator choice
8ca08ffa feat(operations): plan local public tunnel exposure
484a1001 feat(operations): add public alpha ops posture command
f91fd5d0 docs(operations): define public alpha ops posture
51fb88e4 docs(operations): record queue objective decision
cfa7fc96 feat(public-alpha): add local-machine exposure plan gate
2146caa9 feat(local-search): add local-machine staging provision
7d1d0c9c feat(local-search): add public alpha release checks
71964266 feat(local-search): add public read-only alpha mode
f4550d87 feat(search): add governed indexless live fallback
a44b4a72 audit(queue): defer alpha launch for discovery coverage
```

`origin/dev..origin/main` was empty.

## Touched Path Families

The branch diff touches `.aide`, `.github`, `README.md`, `CONTRIBUTING.md`,
`contracts`, `control`, `docs`, `evals`, `examples`, `release`, `runtime`,
`scripts`, `site`, `snapshots`, `surfaces`, `tests`, and `tools`.

## Risk Classification

- `docs_public_front_door`
- `docs_status_navigation`
- `docs_test_guardrail`
- `ops_launch_track`
- `public_alpha_readonly`
- `exposure_plan_only`
- `operator_choice_blocked`
- `generated_artifact_report`
- `runtime_product_foundation`
- `queue_mutation`
- `source_provider_expansion`
- `safe_to_promote_candidate`

## Risk Notes

- Historical queue/control changes are present on `dev`, but this task did not
  mutate `.aide/queue`.
- Bounded source/provider and live metadata pilot work exists on `dev`, but the
  current public posture keeps public live fanout, downloads/uploads, provider
  truth, and public mutation disabled.
- Operator-choice remains `BLOCKED_ON_OPERATOR_PROVIDER_URL`; no tunnel/proxy
  rehearsal has run.
- Root `LICENSE` is absent, so `LICENSE_UNRESOLVED` remains explicit.
- `tmp/` exists as ignored local scratch and is not tracked or touched by this
  task.

## Preflight Decision

Promotion can proceed if focused validators remain green and no public posture
overclaim is introduced.
