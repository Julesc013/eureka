# Full Discovery CI Runbook

Full unittest discovery is a machine or operator lane. AI agents do not run or
babysit it interactively.

## Local Harness

Use:

```bash
python scripts/run_full_unittest_discovery.py
```

By default this writes under `.aide.local/test-runs/<run-id>/`:

- `full_unittest_stdout.txt`
- `full_unittest_stderr.txt`
- `full_unittest_exit_code.txt`
- `full_unittest_summary.json`
- `failure_families.json`
- `failed_tests.txt`
- `paths_touched.txt`
- `environment.json`

Do not commit `.aide.local/`. Commit only compact summary evidence under
`control/audits/` when a closeout or promotion task explicitly needs durable
evidence.

## CI

Use the `Full Discovery` GitHub Actions workflow for manual and scheduled runs.
It uploads the whole `.aide.local/test-runs/...` directory as a short-retention
artifact using `actions/upload-artifact`.

The schedule intentionally avoids minute `0`. Scheduled workflows run on the
default branch and can be delayed or dropped during high-load windows.

## AI Handoff

When full discovery is required during AI work, create an
`external_full_discovery_handoff.v0` file and stop with:

```text
WAITING_FOR_EXTERNAL_FULL_DISCOVERY
```

Return to the AI session with `full_unittest_summary.json`. Do not paste full
stdout or stderr. Ask for targeted traceback excerpts only when the compact
summary is insufficient to repair a failure family.
