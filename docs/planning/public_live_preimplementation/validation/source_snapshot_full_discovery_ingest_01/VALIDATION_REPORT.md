# Validation Report

## Status

`PASS_WITH_WARNINGS`

## Files Created

Required ingest package files were created under:

```text
docs/planning/public_live_preimplementation/validation/source_snapshot_full_discovery_ingest_01/
```

## Full Discovery

Full discovery was not run inside the AI session.

## Protected Paths

This task did not intentionally modify:

- `docs/canon/**`
- `contracts/**`
- `runtime/**`
- `surfaces/**`
- `site/**`
- `snapshots/**`
- `native/**`
- `crates/**`
- `release/**`
- `.aide/queue/current.toml`

## Validation Commands

| Command | Result |
|---|---|
| `git status --short` | PASS, expected new ingest package only |
| `git diff --check` | PASS |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS |
| `python scripts/check_architecture_boundaries.py` | PASS |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | PASS |
| `python -m json.tool TEST_FAILURE_INDEX.json` | PASS |
| `python -m json.tool TEST_ERROR_INDEX.json` | PASS |

## Warnings

- External full discovery is current but red: 45 failures and 1 error.
- The compact failure index has 47 failed-test labels because the harness
  includes synthetic validator-output labels in addition to unittest failure and
  error counts.
- Public alpha remains blocked.
- `dev -> main` promotion remains blocked.
- This task did not run or rerun full discovery inside the AI session.
