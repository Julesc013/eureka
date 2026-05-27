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

Full-discovery output should use an external sibling directory such as
`../eureka-test-runs/<run-id>`, not repo-local `.aide.local/test-runs/`.

Only request targeted traceback excerpts when the compact JSON summary does not
contain enough context to repair a failure family.
