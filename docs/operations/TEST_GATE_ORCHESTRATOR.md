# Test Gate Orchestrator

`scripts/eureka_gate.py` is the preferred operator-facing wrapper for long
external test gates. It keeps full discovery outside AI sessions while reducing
manual steps and producing compact AI handoff bundles.

`scripts/eureka_test_gate.py` remains as the lower-level compatibility wrapper
for the earlier underscore gate names.

## Public Alpha Closeout

Run the gate in the foreground and wait for a compact handoff:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --watch --clean
```

Run it in the background:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --background --clean
```

Check status later:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --status
```

Print the AI handoff after completion:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --handoff
```

Copy or open the handoff:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --handoff --copy
python scripts/eureka_gate.py public-alpha-closeout --handoff --open
```

Copy compact handoff evidence into the matching repo audit folder:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --commit-handoff
```

## Supported Gates

- `public-alpha-closeout`
- `source-snapshot-closeout`
- `promotion-gate`

Each gate writes to:

```text
../eureka-test-runs/<gate-run-id>/
```

The output directory contains the full-discovery compact artifacts plus:

```text
status.json
ai_handoff.json
ai_handoff.md
ai_handoff.zip
```

## Handoff Discipline

`ai_handoff.md` and `ai_handoff.json` are the only artifacts intended for AI
consumption. They contain compact summary data, top failure-family metadata,
failed test counts, git head, and the recommended next step.

Raw unittest stdout and stderr remain local artifacts and should not be pasted
unless a compact failure family is insufficient.

## GitHub Actions

For pushed branch state only:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --github
python scripts/eureka_gate.py public-alpha-closeout --github-status
```

GitHub Actions cannot validate a dirty local candidate tree. Use the local gate
for uncommitted candidate validation.

## Boundaries

- Do not run full discovery inside AI sessions.
- Do not commit `../eureka-test-runs/**`.
- Do not commit raw unittest stdout/stderr.
- Do not use `--git-commit` unless an operator explicitly wants the compact
  handoff commit.
- Do not treat a passing gate as deployment or launch approval.
- Do not auto-run paid AI or Codex from the test gate by default.
