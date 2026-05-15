# AIDE Token Savings Summary

## Method

- approximation: chars / 4, rounded up
- exact_provider_billing: false
- exact_tokenizer: false
- raw_prompt_storage: false
- raw_response_storage: false

## Latest Compact Surfaces

- `.aide/context/latest-task-packet.md`: 3330 chars / 833 approx tokens / within_budget
- `.aide/context/latest-context-packet.md`: 1828 chars / 457 approx tokens / within_budget
- `.aide/context/latest-review-packet.md`: 2174 chars / 544 approx tokens / within_budget
- `.aide/verification/latest-verification-report.md`: 3187 chars / 797 approx tokens / within_budget

## Named Baselines

- `root_history_baseline`: 275993 chars / 68999 approx tokens
- `review_baseline`: 18975 chars / 4744 approx tokens
- `repo_context_baseline`: 243012 chars / 60753 approx tokens

## Compact-To-Baseline Comparisons

- `.aide/context/latest-task-packet.md` vs `root_history_baseline`: 98.8% estimated reduction (833 vs 68999 approx tokens)
- `.aide/context/latest-review-packet.md` vs `review_baseline`: 88.5% estimated reduction (544 vs 4744 approx tokens)
- `.aide/context/latest-context-packet.md` vs `repo_context_baseline`: 99.2% estimated reduction (457 vs 60753 approx tokens)

## Largest Ledger Surfaces

- `.aide/evals/runs/latest-golden-tasks.json` (eval_report): 1871 approx tokens
- `.aide/cache/latest-cache-keys.json` (cache_report): 1793 approx tokens
- `AGENTS.md` (generated_adapter): 1703 approx tokens
- `.aide/prompts/codex-token-mode.md` (baseline_surface): 1593 approx tokens
- `.aide/evals/runs/latest-golden-tasks.md` (eval_report): 1305 approx tokens
- `.aide/prompts/compact-task.md` (baseline_surface): 1000 approx tokens
- `.aide/prompts/evidence-review.md` (baseline_surface): 856 approx tokens
- `.aide/context/latest-task-packet.md` (task_packet): 833 approx tokens
- `.aide/verification/latest-verification-report.md` (verification_report): 797 approx tokens
- `.aide/cache/latest-cache-keys.md` (cache_report): 716 approx tokens

## Budget Warnings

- none

## Regression Warnings

- none

## Uncertainty

These are estimated metadata records only. They do not measure provider billing, exact tokenizer behavior, hidden reasoning tokens, cached-token discounts, or quality outcomes. Q15 golden tasks provide deterministic local quality gates, but they do not prove arbitrary coding-task quality.
