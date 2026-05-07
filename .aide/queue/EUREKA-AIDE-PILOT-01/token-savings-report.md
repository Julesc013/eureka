# Token Savings Report

## Compact Packet

- Latest task packet: `.aide/context/latest-task-packet.md`.
- Chars: 3792.
- Approx tokens: 948.
- Method: `chars / 4`, rounded up.

Optional compact surfaces:

- `.aide/context/latest-context-packet.md`: 1808 chars / 452 approx tokens.
- `.aide/context/latest-review-packet.md`: 4208 chars / 1052 approx tokens.
- `.aide/verification/latest-verification-report.md`: 4572 chars / 1143 approx tokens.

## Naive Baseline

Baseline name: `root_history_baseline`.

Included local files:

- `README.md`
- `AGENTS.md`
- `docs/README.md`
- `docs/ROADMAP.md`
- `docs/BOOTSTRAP_STATUS.md`
- `docs/operations/TEST_AND_EVAL_LANES.md`
- `control/inventory/tests/README.md`
- `.aide/memory/project-state.md`

Baseline chars: 274587.
Baseline approx tokens: 68647.

## Result

- Compact packet approx tokens: 948.
- Naive baseline approx tokens: 68647.
- Estimated reduction: 98.6%.

This is an estimate only. It does not claim exact tokenizer behavior, provider
billing, reasoning-token usage, cached-token discounts, or quality equivalence
for arbitrary future tasks.

## Quality Caveat

The reduction is acceptable only because the packet preserves objective,
context refs, allowed/forbidden paths, validation, evidence, non-goals,
acceptance, and output schema. It should not be treated as a license to remove
load-bearing task details.
