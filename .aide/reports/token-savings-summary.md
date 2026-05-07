# AIDE Token Savings Summary

## Method

- approximation: chars / 4, rounded up
- exact_provider_billing: false
- exact_tokenizer: false
- raw_prompt_storage: false
- raw_response_storage: false

## Latest Compact Surfaces

- `.aide/context/latest-task-packet.md`: 3792 chars / 948 approx tokens / within_budget
- `.aide/context/latest-context-packet.md`: 1807 chars / 452 approx tokens / within_budget
- `.aide/context/latest-review-packet.md`: 5340 chars / 1335 approx tokens / within_budget
- `.aide/verification/latest-verification-report.md`: 5571 chars / 1393 approx tokens / within_budget

## Named Baselines

- `root_history_baseline`: 274390 chars / 68598 approx tokens
- `review_baseline`: 19545 chars / 4887 approx tokens
- `repo_context_baseline`: 239176 chars / 59794 approx tokens

## Compact-To-Baseline Comparisons

- `.aide/context/latest-task-packet.md` vs `root_history_baseline`: 98.6% estimated reduction (948 vs 68598 approx tokens)
- `.aide/context/latest-review-packet.md` vs `review_baseline`: 72.7% estimated reduction (1335 vs 4887 approx tokens)
- `.aide/context/latest-context-packet.md` vs `repo_context_baseline`: 99.2% estimated reduction (452 vs 59794 approx tokens)

## Largest Ledger Surfaces

- `.aide/cache/latest-cache-keys.json` (cache_report): 2008 approx tokens
- `.aide/prompts/codex-token-mode.md` (baseline_surface): 1593 approx tokens
- `.aide/verification/latest-verification-report.md` (verification_report): 1393 approx tokens
- `AGENTS.md` (generated_adapter): 1370 approx tokens
- `.aide/context/latest-review-packet.md` (review_packet): 1335 approx tokens
- `.aide/prompts/compact-task.md` (baseline_surface): 1000 approx tokens
- `.aide/context/latest-task-packet.md` (task_packet): 948 approx tokens
- `.aide/prompts/evidence-review.md` (baseline_surface): 856 approx tokens
- `.aide/evals/runs/latest-golden-tasks.json` (eval_report): 813 approx tokens
- `.aide/cache/latest-cache-keys.md` (cache_report): 716 approx tokens

## Budget Warnings

- near budget: cache_report `.aide/cache/latest-cache-keys.json` 2008/2400

## Regression Warnings

- none

## Uncertainty

These are estimated metadata records only. They do not measure provider billing, exact tokenizer behavior, hidden reasoning tokens, cached-token discounts, or quality outcomes. Q15 golden tasks provide deterministic local quality gates, but they do not prove arbitrary coding-task quality.
