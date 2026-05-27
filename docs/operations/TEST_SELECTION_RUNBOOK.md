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

When full discovery is selected, run the selected harness command instead of
running `python -m unittest discover -s tests -t .` directly in an AI session:

```bash
python scripts/run_full_unittest_discovery.py
```

The harness writes compact results to
`../eureka-test-runs/<timestamp>/full_unittest_summary.json` by default, or
to the path passed with `--out`. Keep full-discovery output outside the repo;
commit compact audit evidence separately when a reviewed closeout or promotion
task needs durable evidence.

If a runtime task defers full discovery, record the deferral and run full
discovery before promotion or another high-risk runtime bridge.

