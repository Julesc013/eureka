# Test Selection Runbook

Use the selector before choosing validation by hand:

```bash
python scripts/eureka_test_select.py --changed --failed-first --json
```

Useful modes:

- `--changed`: inspect staged, unstaged, and untracked paths.
- `--since <ref>`: inspect paths changed since a ref.
- `--task <task-id>`: select task-mapped lanes.
- `--failed-first`: put active failure-ledger reruns before broad suites.
- `--promotion`: include full discovery and promotion checks.
- `--full`: include full unittest discovery without a promotion decision.

The selector does not run tests. It selects commands and records skip reasons.
The operator still runs the selected commands and records their outcome.

If a runtime task defers full discovery, record the deferral and run full
discovery before promotion or another high-risk runtime bridge.

