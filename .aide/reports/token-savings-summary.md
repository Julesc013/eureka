# AIDE Token Savings Summary

## Method

- approximation: chars / 4, rounded up
- exact_provider_billing: false
- exact_tokenizer: false
- raw_prompt_storage: false
- raw_response_storage: false

## Latest Compact Surfaces

- `.aide/context/latest-task-packet.md`: 4796 chars / 1199 approx tokens / within_budget
- `.aide/context/latest-context-packet.md`: 1828 chars / 457 approx tokens / within_budget
- `.aide/context/latest-review-packet.md`: 4899 chars / 1225 approx tokens / within_budget
- `.aide/verification/latest-verification-report.md`: 4572 chars / 1143 approx tokens / within_budget

## Named Baselines

- `root_history_baseline`: 275165 chars / 68792 approx tokens
- `review_baseline`: 21035 chars / 5259 approx tokens
- `repo_context_baseline`: 242184 chars / 60546 approx tokens

## Compact-To-Baseline Comparisons

- `.aide/context/latest-task-packet.md` vs `root_history_baseline`: 98.3% estimated reduction (1199 vs 68792 approx tokens)
- `.aide/context/latest-review-packet.md` vs `review_baseline`: 76.7% estimated reduction (1225 vs 5259 approx tokens)
- `.aide/context/latest-context-packet.md` vs `repo_context_baseline`: 99.2% estimated reduction (457 vs 60546 approx tokens)

## Largest Ledger Surfaces

- `.aide/cache/latest-cache-keys.json` (cache_report): 2008 approx tokens
- `.aide/evals/runs/latest-golden-tasks.json` (eval_report): 1599 approx tokens
- `.aide/prompts/codex-token-mode.md` (baseline_surface): 1593 approx tokens
- `AGENTS.md` (generated_adapter): 1498 approx tokens
- `.aide/context/latest-review-packet.md` (review_packet): 1225 approx tokens
- `.aide/context/latest-task-packet.md` (task_packet): 1199 approx tokens
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
