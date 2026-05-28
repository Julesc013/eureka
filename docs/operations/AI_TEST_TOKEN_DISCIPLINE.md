# AI Test Token Discipline

AI agents must not babysit long-running test commands.

Commands expected to exceed 120 seconds must use a harness or CI. Full unittest
discovery must not run inside AI sessions by default.

During AI development, use focused lanes:

```bash
python scripts/eureka_test_select.py --changed --failed-first --json
```

If full discovery is required, write an external handoff and stop with
`WAITING_FOR_EXTERNAL_FULL_DISCOVERY`. The operator or CI runs the long command,
then returns `full_unittest_summary.json`, not full logs.

Foreground operator command:

```bash
python scripts/run_full_unittest_discovery.py --out ../eureka-test-runs/<run-id>
```

Background operator commands:

```bash
python scripts/start_full_discovery.py --run-id <run-id>
python scripts/check_full_discovery.py --run-id <run-id>
```

To wait without AI polling and print compact handoff artifacts at completion:

```bash
python scripts/check_full_discovery.py --run-id <run-id> --watch --interval-seconds 300 --handoff
```

Full-discovery output should use an external sibling directory such as
`../eureka-test-runs/<run-id>`, not repo-local `.aide.local/test-runs/`.

Only request targeted traceback excerpts when the compact JSON summary does not
contain enough context to repair a failure family.
