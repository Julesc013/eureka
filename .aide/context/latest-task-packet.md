# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-REASSESS-00 - product-readiness reassessment

## GOAL

Reassess whether public alpha should proceed toward launch after refreshed seed
snapshots. The expected honest outcome is to keep launch deferred while
recording that the current projection is useful for internal demo and operator
review.

## WHY

The public alpha routes and read-only projections are structurally present, but
the refreshed snapshot has only 1 reviewed record and 28 review-only
candidates. Product usefulness must be measured separately from route
correctness.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/snapshot_refresh_result.json`
- `examples/snapshots/refresh/snapshot_refresh_result.json`
- `control/inventory/public_alpha_readonly_00_result.json`
- `control/inventory/public_alpha_launch_defer_result.json`

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-ALPHA-REASSESS-00/**`
- `.aide/queue/LIVE-METADATA-PILOT-BATCH-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-01/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-01/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/**`
- `contracts/publication/**`
- `runtime/public_alpha/**`
- `scripts/eureka_public_alpha_reassess.py`
- `scripts/eureka_public_alpha_reassess_report.py`
- `scripts/eureka_public_alpha_route_smoke.py`
- `scripts/validate_public_alpha_reassess.py`
- `tests/runtime/test_public_alpha_reassess*.py`
- `tests/operations/test_public_alpha_reassess_scripts.py`
- `tests/scripts/test_validate_public_alpha_reassess.py`
- `examples/public_alpha/reassess/**`
- `control/policies/public_alpha_reassess*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_alpha_reassess*.json`
- `control/audits/public-alpha-reassess-00-v0/**`
- `docs/architecture/PUBLIC_ALPHA_REASSESS.md`
- `docs/operations/PUBLIC_ALPHA_REASSESS_RUNBOOK.md`
- `docs/operations/PUBLIC_ALPHA_USEFULNESS_THRESHOLDS.md`
- `docs/operations/POST_PUBLIC_ALPHA_REASSESS_PLAN.md`
- `docs/reference/PUBLIC_ALPHA_REASSESS_DECISION.md`
- `docs/reference/PUBLIC_ALPHA_USEFULNESS_METRICS.md`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `../eureka-test-runs/**`
- `secrets/**`
- `.env`
- private local files
- committed operator tokens
- provider credentials
- raw live source responses
- raw IA responses
- raw full-discovery stdout/stderr logs
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Add deterministic public-alpha reassessment runtime over snapshot-refresh
  examples.
- Add contracts, policies, metrics/matrices, examples, docs, validator, scripts,
  tests, and audit evidence.
- Record conservative launch blockers and next-work recommendations.
- Update queue state to recommend `LIVE-METADATA-PILOT-BATCH-00`.

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_alpha_reassess.py`
- focused prior validators for snapshot refresh, seed batches, review batch,
  SCOUT, candidate index, query planner, snapshot relay, public alpha read-only,
  source action kernel, and source wave
- focused public-alpha reassess unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit
  check when practical

Full unittest discovery is not run by policy.

## COMMITS

Use commit message:

```text
product(public): reassess alpha after seed snapshots
```

## EVIDENCE

- `control/inventory/public_alpha_reassess_result.json`
- `control/inventory/public_alpha_reassess_boundary_report.json`
- `control/audits/public-alpha-reassess-00-v0/`
- `examples/public_alpha/reassess/public_alpha_reassess_decision.json`

## NON_GOALS

- No deployment.
- No public launch.
- No production-readiness claim.
- No public-launch-readiness claim.
- No candidate acceptance or reviewed-index mutation.
- No public/master index mutation.
- No site-dist write.
- No live source calls, source probes, downloads, extraction, or model calls.

## ACCEPTANCE

- Reassessment records reviewed records: 1, candidates: 28, known needs: 28,
  bounded absence summaries: 2.
- `launch_recommended` is false.
- `demo_mode_recommended` is true.
- `needs_more_reviewed_records`, `needs_more_seed_batches`, and
  `needs_live_metadata_pilot` are true.
- Boundary flags remain false.
- Recommended next task is `LIVE-METADATA-PILOT-BATCH-00`.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `PUBLIC_ALPHA_REASSESS`, `VALIDATION`,
`BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 1050
- budget_status: PASS
