# Source Foundry Preview v0 Full Discovery Ingest

## Status

PASS

## External Run

| Field | Value |
| --- | --- |
| Run ID | `source_foundry_preview_v0_post_historical_repair_02` |
| Command | `python -m unittest discover -s tests -t .` |
| Tested branch | `dev` |
| Tested commit | `bad6bf6d954cc4f497079e97cab946b11dde404d` |
| Current `dev` commit at ingest | `bad6bf6d954cc4f497079e97cab946b11dde404d` |
| Repair commit | `1ceeed045b7fb8afa24485545525aeeaadb64507` |
| Started | `2026-06-19T07:01:08Z` |
| Finished | `2026-06-19T07:51:24Z` |
| Duration | 3016.383891 seconds |
| Tests | 5,793 |
| Failures | 0 |
| Errors | 0 |
| Skipped | 0 |
| Exit code | 0 |

## Previous Red-Run Comparison

The previous checkpoint run `source_foundry_preview_v0_checkpoint_00` reported:

| Run | Tests | Failures | Errors | Exit code |
| --- | ---: | ---: | ---: | ---: |
| `source_foundry_preview_v0_checkpoint_00` | 5,792 | 43 | 7 | 1 |
| `source_foundry_preview_v0_post_historical_repair_02` | 5,793 | 0 | 0 | 0 |

The expected count drift is explained by the handoff: one repository-layout
validator regression test was added during the historical drift repair.

## Repair Posture

- Runtime leakage repair: PASS, zero new unallowlisted violations.
- Historical validator drift repair: READY_FOR_EXTERNAL_FULL_DISCOVERY_RERUN.
- External rerun: PASS.
- Main promotion: not performed in this task.

## Safety Posture

- Reviewed IA truth created: false.
- Reviewed records created: false.
- Reviewed/master mutation: false.
- Public-index mutation: false.
- Candidate-index store mutation: false.
- Evidence-ledger store mutation: false.
- Review decisions changed: false.
- Snapshot publication: false.
- Public exposure: paused.
- Public launch: false.
- Production readiness claim: false.
- License posture: unchanged.

## Focused Guardrails

- `python scripts/check_architecture_boundaries.py`: PASS.
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: PASS before adding this audit packet.
- `python scripts/validate_runtime_architecture_leakage.py --json`: PASS.
- `python scripts/validate_public_alpha_readonly.py`: PASS.
- `python scripts/validate_snapshot_relay.py`: PASS.
- `git diff --check`: PASS before adding this audit packet.

## Promotion Readiness

The green full-discovery result is valid promotion evidence for the Source
Foundry Preview v0 tooling checkpoint. Promotion remains a separate task and
must preserve this wording:

```text
Source Foundry Preview v0 is functional and validated.
IA candidates remain unreviewed or evidence-requested.
No reviewed IA truth has been created.
Public exposure remains paused.
```

Recommended next task:

```text
DEV-TO-MAIN-SOURCE-FOUNDRY-PREVIEW-V0-00
```

