# Test Gate Orchestrator

`scripts/eureka_test_gate.py` is the operator-facing wrapper for long external
test gates. It keeps full discovery outside AI sessions while reducing manual
steps.

## Public Alpha Closeout

Run the gate in the foreground and wait for a compact handoff:

```powershell
python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --watch --clean
```

Run it in the background:

```powershell
python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --background --clean
```

Check status later:

```powershell
python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --status
```

Print the AI handoff after completion:

```powershell
python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --handoff
```

## Supported Gates

- `public_alpha_readonly_closeout`
- `source_snapshot_closeout`
- `promotion_gate`

Each gate writes to:

```text
../eureka-test-runs/<gate>/
```

The output directory contains the full-discovery compact artifacts plus:

```text
status.json
ai_handoff.md
```

## Handoff Discipline

`ai_handoff.md` is the only artifact intended to paste into an AI session. It
contains compact summary data, failure-family data only when needed, failed test
names only when needed, `git status --short --branch`, and the recommended next
step.

Raw unittest stdout and stderr remain local artifacts and should not be pasted
unless a compact failure family is insufficient.

## GitHub Actions

For pushed branch state only:

```powershell
python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --github
python scripts/eureka_test_gate.py --gate public_alpha_readonly_closeout --github-status
```

GitHub Actions cannot validate a dirty local candidate tree. Use the local gate
for uncommitted candidate validation.

## Boundaries

- Do not run full discovery inside AI sessions.
- Do not commit `../eureka-test-runs/**`.
- Do not commit raw unittest stdout/stderr.
- Do not treat a passing gate as deployment or launch approval.
- Do not auto-run paid AI or Codex from the test gate by default.
