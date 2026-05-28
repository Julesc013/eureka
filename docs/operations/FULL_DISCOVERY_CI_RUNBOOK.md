# Full Discovery CI Runbook

Full unittest discovery is a machine or operator lane. AI agents do not run or
babysit it interactively.

## Local Harness

Use:

```bash
python scripts/run_full_unittest_discovery.py
```

The harness prints an immediate start banner and compact heartbeat progress to
the operator terminal while raw unittest stdout and stderr stay in artifact
files. Silent mode requires `--quiet`. For shorter heartbeat intervals during
manual runs, use:

```bash
python scripts/run_full_unittest_discovery.py --heartbeat-seconds 10
```

By default this writes under `../eureka-test-runs/<run-id>/`:

- `full_unittest_stdout.txt`
- `full_unittest_stderr.txt`
- `full_unittest_exit_code.txt`
- `full_unittest_summary.json`
- `failure_families.json`
- `failed_tests.txt`
- `paths_touched.txt`
- `environment.json`
- `status.json`

Do not write full-discovery artifacts under repo-local private roots such as
`.aide.local/`. The harness refuses those roots unless
`--allow-repo-local-output` is supplied for exceptional debugging. Commit only
compact summary evidence under `control/audits/` when a closeout or promotion
task explicitly needs durable evidence.

## Background Local Run

To avoid tying up the terminal or AI session, start a detached local run:

```powershell
python scripts/start_full_discovery.py --run-id public_alpha_readonly_closeout
```

Check it later without reading raw logs:

```powershell
python scripts/check_full_discovery.py --run-id public_alpha_readonly_closeout
```

The check command reads `status.json` and the compact summary when present. The
AI session should not monitor the process. When it completes, paste only
`full_unittest_summary.json`, `failure_families.json`, `failed_tests.txt`, and
`git status --short --branch`.

## CI

Use the `Full Discovery` GitHub Actions workflow for manual and scheduled runs.
It uploads the whole `../eureka-test-runs/...` directory as a short-retention
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
