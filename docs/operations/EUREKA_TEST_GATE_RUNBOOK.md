# Eureka Test Gate Runbook

`scripts/eureka_gate.py` is the preferred operator-facing command for long
Eureka validation gates. It keeps raw full-discovery logs outside the repo,
produces compact AI handoff files, and avoids AI token waste.

## Gates

Supported gate names:

- `public-alpha-closeout`
- `source-snapshot-closeout`
- `promotion-gate`

The command also accepts the older underscore run ids as aliases. Gate output
defaults to the stable external run directory under:

```text
../eureka-test-runs/<gate-run-id>/
```

## Run

Foreground with progress and final handoff:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --watch --clean
```

Background:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --background --clean
```

Check status later:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --status
```

Print the compact handoff:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --handoff
```

Copy or open the handoff:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --handoff --copy
python scripts/eureka_gate.py public-alpha-closeout --handoff --open
```

## Handoff Files

Completed gates write:

```text
ai_handoff.json
ai_handoff.md
ai_handoff.zip
```

The handoff contains counts, status, git head, top failure-family metadata,
recommended next task, and a paste-ready AI summary. It does not include raw
unittest stdout or stderr.

## Commit-Safe Handoff

For ChatGPT or GitHub connector workflows where the AI cannot read local
external files, copy only compact handoff evidence into the repo:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --commit-handoff
```

This writes the matching `control/audits/**/external_gate_*` files and refreshes
the compact inventory full-discovery result. It prints the exact repo paths but
does not run `git commit` unless `--git-commit` is explicitly supplied.

Forbidden in commit-safe mode:

- raw unittest stdout/stderr
- `../eureka-test-runs/**`
- `.aide.local/**`
- local instance state
- secrets or operator tokens

## GitHub Actions

For pushed branch state only:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --github
python scripts/eureka_gate.py public-alpha-closeout --github-status
```

Use local gates for dirty candidate trees. GitHub Actions cannot validate
uncommitted local changes.
