# Secret Scan Summary

Target paths: `.aide`, root guidance/docs, product roots, scripts, tests, and `.gitignore`.

- `broad`: matches=3541, exit=0
- `long-openai-key-shape`: matches=1, exit=0
- `anthropic-key-shape`: matches=0, exit=1
- `private-key-block`: matches=2, exit=0
- `env-secret-assignment`: matches=0, exit=1

Inspection result: matches are policy, documentation, test, schema, or fake fixture strings. No committed high-confidence live provider secret assignment was found in Q56-scoped review.

Samples were inspected in terminal output and not committed verbatim to avoid preserving any possible secret text in evidence.
