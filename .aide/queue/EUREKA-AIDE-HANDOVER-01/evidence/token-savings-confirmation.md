# Token Savings Confirmation

## Current Compact Packet

- Latest task packet: `.aide/context/latest-task-packet.md`.
- Task: `EUREKA-AIDE-SELFTEST-01 - Repair imported AIDE Lite selftest fixture fallback`.
- Chars: 5767.
- Approx tokens: 1442.
- Method: `chars / 4`, rounded up.
- Budget status: PASS / within budget.

Optional compact surfaces after Q26 regeneration:

- `.aide/context/latest-context-packet.md`: 1827 chars / 457 approx tokens.
- `.aide/context/latest-review-packet.md`: 5394 chars / 1349 approx tokens.

Previous Q22 packet:

- `.aide/context/latest-task-packet.md`: 3792 chars / 948 approximate tokens.

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

Current same-file baseline chars: 277363.
Current same-file baseline approx tokens: 69341.

Historical Q22 baseline chars: 274587.
Historical Q22 baseline approx tokens: 68647.

## Result

- Compact packet approx tokens: 1442.
- Current same-file naive baseline approx tokens: 69341.
- Estimated reduction against current same-file baseline: 97.9%.
- Estimated reduction against historical Q22 baseline: 97.9%.

Q26's packet is larger than the Q22 generic audit packet because it contains a
concrete first-task handoff with allowed paths, forbidden paths, validation,
evidence, acceptance, and output schema. The reduction remains material.

This is an approximate prompt-size estimate only. It does not claim exact
tokenizer behavior, provider billing reduction, cached-token discounts,
reasoning-token behavior, or equivalent quality for arbitrary future work.
