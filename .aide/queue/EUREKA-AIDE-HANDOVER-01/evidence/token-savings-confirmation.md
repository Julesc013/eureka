# Token Savings Confirmation

## Current Compact Packet

- Latest task packet: `.aide/context/latest-task-packet.md`.
- Task: `LOCAL-04 - Read-only localhost HTTP service over reviewed index`.
- Chars: 6157.
- Approx tokens: 1540.
- Method: `chars / 4`, rounded up.
- Budget status: PASS / within budget.

Optional compact surfaces after Q26 revalidation:

- `.aide/context/latest-context-packet.md`: 1832 chars / 458 approx tokens.
- `.aide/context/latest-review-packet.md`: 6717 chars / 1680 approx tokens.

Previous packets:

- Q22 generic packet: 3792 chars / 948 approx tokens.
- Earlier Q26 selftest repair packet: 5767 chars / 1442 approx tokens.

## Baseline

Q26 reuses the same local baseline family recorded by Q22:

- `README.md`
- `AGENTS.md`
- `docs/README.md`
- `docs/ROADMAP.md`
- `docs/BOOTSTRAP_STATUS.md`
- `docs/operations/TEST_AND_EVAL_LANES.md`
- `control/inventory/tests/README.md`
- `.aide/memory/project-state.md`

Current same-file baseline chars: 274729.
Current same-file baseline approx tokens: 68683.

Historical Q22 baseline chars: 274587.
Historical Q22 baseline approx tokens: 68647.

## Result

- Compact packet approx tokens: 1540.
- Current same-file naive baseline approx tokens: 68683.
- Estimated reduction against current same-file baseline: 97.8%.
- Estimated reduction against historical Q22 baseline: 97.8%.

The current packet is larger than the Q22 pilot packet because it contains a
concrete LOCAL-04 handoff plus the newly discovered validation preflight blocker.
The reduction remains material.

This is an approximate prompt-size estimate only. It does not claim exact
tokenizer behavior, provider billing reduction, cached-token discounts,
reasoning-token behavior, or equivalent quality for arbitrary future work.
