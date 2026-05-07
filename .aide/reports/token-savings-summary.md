# AIDE Token Savings Summary

## Method

- approximation: chars / 4, rounded up
- exact_provider_billing: false
- exact_tokenizer: false
- raw_prompt_storage: false
- raw_response_storage: false

## Latest Compact Surfaces

- `.aide/context/latest-task-packet.md`: 4722 chars / 1181 approx tokens / within_budget
- `.aide/context/latest-context-packet.md`: 1828 chars / 457 approx tokens / within_budget
- `.aide/context/latest-review-packet.md`: 5277 chars / 1320 approx tokens / within_budget
- `.aide/verification/latest-verification-report.md`: 4572 chars / 1143 approx tokens / within_budget

## Named Baselines

- `root_history_baseline`: 274754 chars / 68689 approx tokens
- `review_baseline`: 20350 chars / 5088 approx tokens
- `repo_context_baseline`: 241740 chars / 60435 approx tokens

## Compact-To-Baseline Comparisons

- `.aide/context/latest-task-packet.md` vs `root_history_baseline`: 98.3% estimated reduction (1181 vs 68689 approx tokens)
- `.aide/context/latest-review-packet.md` vs `review_baseline`: 74.1% estimated reduction (1320 vs 5088 approx tokens)
- `.aide/context/latest-context-packet.md` vs `repo_context_baseline`: 99.2% estimated reduction (457 vs 60435 approx tokens)

## Largest Ledger Surfaces

- `.aide/cache/latest-cache-keys.json` (cache_report): 2008 approx tokens
- `.aide/evals/runs/latest-golden-tasks.json` (eval_report): 1599 approx tokens
- `.aide/prompts/codex-token-mode.md` (baseline_surface): 1593 approx tokens
- `AGENTS.md` (generated_adapter): 1370 approx tokens
- `.aide/context/latest-review-packet.md` (review_packet): 1320 approx tokens
- `.aide/context/latest-task-packet.md` (task_packet): 1181 approx tokens
- `.aide/verification/latest-verification-report.md` (verification_report): 1143 approx tokens
- `.aide/evals/runs/latest-golden-tasks.md` (eval_report): 1118 approx tokens
- `.aide/prompts/compact-task.md` (baseline_surface): 1000 approx tokens
- `.aide/prompts/evidence-review.md` (baseline_surface): 856 approx tokens

## Budget Warnings

- near budget: cache_report `.aide/cache/latest-cache-keys.json` 2008/2400

## Regression Warnings

- none

## Uncertainty

These are estimated metadata records only. They do not measure provider billing, exact tokenizer behavior, hidden reasoning tokens, cached-token discounts, or quality outcomes. Q15 golden tasks provide deterministic local quality gates, but they do not prove arbitrary coding-task quality.
