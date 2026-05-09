# Merge Plan

Proposed convergence branch: `sync/eureka-convergence-20260509`

This audit did not create the convergence branch because the conflict risk is high.

## Recommended Plan

1. Review OBS-AGENT-01 through OBS-AGENT-07 remote artifacts against local Track B artifacts.
2. Decide whether remote SearchNeed seed and WorkUnit seed contracts remain valid, are superseded by Track B SearchNeed/WorkUnit runtimes, or should coexist as reviewed seed inputs.
3. Reconcile overlapping observation candidate review queue files, inventories, validators, and tests.
4. Reconcile stale `.aide/context/*` and `.aide/evals/runs/latest-golden-tasks.*` files after semantic decisions are made.
5. Create `sync/eureka-convergence-20260509` only after the review plan is explicit.
6. Merge or cherry-pick by reviewed lane, not by guessing from Git's automatic text merge.
7. Run full Track B plus OBS validators after convergence.

## Branches Skipped

- `main`: skipped because direct merge into main is forbidden for this task.
- `origin/main`: fetched and audited but not merged because of high semantic overlap.

## Human Review Needed

- Whether OBS seed artifacts should be retained alongside Track B local foundry runtimes.
- Whether local Track B B07-B23 work should be replayed onto remote main as-is or split into reviewed task commits.
- Whether the preservation commit should be kept as evidence only or replaced by cleaner reviewed commits during a future convergence.
