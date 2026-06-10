# Example Next Turn Prompt

This prompt is the safe product continuation when external artifact evidence has
not yet returned. It does not ask the AI session to collect evidence directly.

````text
# EXTERNAL-ARTIFACT-EVIDENCE-RETURN-00

Use this prompt from the repository root only after the compact external return
file exists.

## Goal

Inspect the returned external/manual artifact evidence summary and decide
whether the repo can safely resume at `MANUAL-ARTIFACT-OBSERVATION-BATCH-03`.

## Required Return File

```text
../eureka-evidence-runs/artifact_evidence_collection_00/artifact_evidence_collection_summary.json
```

## Required Reading

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `docs/reference/artifact_evidence_collection_handoff_00/README.md`
- `docs/reference/artifact_evidence_collection_handoff_00/return_contract.md`
- `docs/reference/artifact_evidence_collection_handoff_00/blocked_and_waiting.md`
- `docs/reference/artifact_evidence_gap_batch_01/gate_status.md`

## Hard Constraints

Do not perform source probes, scraping, crawling, downloads, executable fetches,
installs, execution, extraction, emulation, public-alpha launch, deployment, or
`dev -> main` promotion.

Do not create reviewed artifact records or verified artifacts in this return
inspection task. The return only decides whether the next observation batch can
start.

## Validation

Run:

```powershell
python scripts/check_git_task_state.py --mode start-task --task-id EXTERNAL-ARTIFACT-EVIDENCE-RETURN-00
git diff --check
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
py -3 scripts/eureka_test_select.py --changed --failed-first --json
```

Run focused tests if the selector recommends them.

## Expected Outcome

If the return file is present and conforms to the contract, report:

```text
next_task: MANUAL-ARTIFACT-OBSERVATION-BATCH-03
```

If the return file is missing or incomplete, stop with:

```text
WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE
```

If the Windows 98 driver target still lacks device details, keep:

```text
WAITING_FOR_USER_HARDWARE_DETAILS
```
````
