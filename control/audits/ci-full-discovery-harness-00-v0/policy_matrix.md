# Policy Matrix

- AI agents must not babysit long-running test commands.
- Commands expected to exceed 120 seconds use harness or CI.
- Full unittest discovery is manual, nightly, or promotion evidence.
- AI reads compact JSON summaries, not full logs.
