# Dev To Main Source Foundry Preview v0

## Status

PASS

## Milestone

```text
Source Foundry Preview v0
```

Promotion wording:

```text
Source Foundry Preview v0 is functional and validated.
IA candidates remain unreviewed or evidence-requested.
No reviewed IA truth has been created.
Public exposure remains paused.
```

## Branch Result

| Field | Value |
| --- | --- |
| Promotion method | fast-forward only |
| Source branch | `dev` |
| Target branch | `main` |
| `origin/main` before | `3b770ab9a9f6a99572f66c3ab2b89fb4e6fddf31` |
| Promoted checkpoint | `f925d18d89dc1ed33c54b170d6d0408b6539f360` |
| `origin/main` after checkpoint fast-forward | `f925d18d89dc1ed33c54b170d6d0408b6539f360` |
| `origin/dev` after checkpoint fast-forward | `f925d18d89dc1ed33c54b170d6d0408b6539f360` |
| `origin/main...origin/dev` after checkpoint fast-forward | `0 0` |
| Promoted commit count before report commit | 30 |
| Promoted changed-path count before report commit | 226 |

This audit packet is a docs/control descendant of the promoted checkpoint. It
does not change product runtime behavior or broaden the milestone claim.

## Validation Evidence

External full-discovery ingest:

| Field | Value |
| --- | --- |
| Run ID | `source_foundry_preview_v0_post_historical_repair_02` |
| Tested commit | `bad6bf6d954cc4f497079e97cab946b11dde404d` |
| Ingest commit | `f925d18d89dc1ed33c54b170d6d0408b6539f360` |
| Tests | 5,793 |
| Failures | 0 |
| Errors | 0 |
| Exit code | 0 |

The external run tested `bad6bf6d954cc4f497079e97cab946b11dde404d`. The
promoted checkpoint `f925d18d89dc1ed33c54b170d6d0408b6539f360` is a docs/control
ingest descendant that records the green compact artifacts.

## Focused Guardrails

Before promotion:

- `python scripts/check_git_task_state.py --mode start-task --task-id DEV-TO-MAIN-SOURCE-FOUNDRY-PREVIEW-V0-00`: PASS with branch-name warning only.
- `python scripts/check_full_discovery.py --run-id source_foundry_preview_v0_post_historical_repair_02 --json`: PASS.
- `python scripts/check_architecture_boundaries.py`: PASS.
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: PASS.
- `python scripts/validate_runtime_architecture_leakage.py --json`: PASS.
- `python scripts/validate_public_alpha_readonly.py`: PASS.
- `python scripts/validate_snapshot_relay.py`: PASS.
- `git diff --check`: PASS.

## Non-Claims

- Reviewed IA truth created: false.
- Reviewed records created: false.
- Reviewed/master mutation: false.
- Public-index mutation: false.
- Candidate-index store mutation: false.
- Evidence-ledger store mutation: false.
- Review decision changes in this task: false.
- Snapshot publication: false.
- Public exposure: paused.
- Public launch: false.
- Production readiness claim: false.
- License posture: unchanged.

## Next

The next strategic task is:

```text
HUMAN-LAST-E2E-REFERENCE-BUILD-00
```

That task should record the operating decision to pause routine human review of
real candidates while the coherent local reference experience is built.

