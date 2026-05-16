# AIDE Token Savings Summary

## Method

- approximation: chars / 4, rounded up
- exact_provider_billing: false
- exact_tokenizer: false
- raw_prompt_storage: false
- raw_response_storage: false

## Latest Compact Surfaces

- `.aide/context/latest-task-packet.md`: 4124 chars / 1031 approx tokens / within_budget
- `.aide/context/latest-context-packet.md`: 1836 chars / 459 approx tokens / within_budget
- `.aide/context/latest-review-packet.md`: 6666 chars / 1667 approx tokens / within_budget
- `.aide/verification/latest-verification-report.md`: 3444 chars / 861 approx tokens / within_budget

## Named Baselines

- `root_history_baseline`: 276460 chars / 69115 approx tokens
- `review_baseline`: 20371 chars / 5093 approx tokens
- `repo_context_baseline`: 243754 chars / 60939 approx tokens

## Compact-To-Baseline Comparisons

- `.aide/context/latest-task-packet.md` vs `root_history_baseline`: 98.5% estimated reduction (1031 vs 69115 approx tokens)
- `.aide/context/latest-review-packet.md` vs `review_baseline`: 67.3% estimated reduction (1667 vs 5093 approx tokens)
- `.aide/context/latest-context-packet.md` vs `repo_context_baseline`: 99.2% estimated reduction (459 vs 60939 approx tokens)

## Largest Ledger Surfaces

- `.aide/evals/runs/latest-golden-tasks.json` (eval_report): 16455 approx tokens
- `.aide/evals/runs/latest-golden-tasks.md` (eval_report): 11267 approx tokens
- `.aide/cache/latest-cache-keys.json` (cache_report): 2008 approx tokens
- `AGENTS.md` (generated_adapter): 1788 approx tokens
- `.aide/context/latest-review-packet.md` (review_packet): 1667 approx tokens
- `.aide/prompts/codex-token-mode.md` (baseline_surface): 1593 approx tokens
- `.aide/context/latest-task-packet.md` (task_packet): 1031 approx tokens
- `.aide/prompts/compact-task.md` (baseline_surface): 1000 approx tokens
- `.aide/verification/latest-verification-report.md` (verification_report): 861 approx tokens
- `.aide/prompts/evidence-review.md` (baseline_surface): 856 approx tokens

## Budget Warnings

- over budget: eval_report `.aide/evals/runs/latest-golden-tasks.json` 16455/4800
- over budget: eval_report `.aide/evals/runs/latest-golden-tasks.md` 11267/4800

## Budget Watchlist

- near budget: cache_report `.aide/cache/latest-cache-keys.json` 2008/2400

## Regression Warnings

- none

## Uncertainty

These are estimated metadata records only. They do not measure provider billing, exact tokenizer behavior, hidden reasoning tokens, cached-token discounts, or quality outcomes. Q15 golden tasks provide deterministic local quality gates, but they do not prove arbitrary coding-task quality.
