# E2E Reference System Track Operations

This runbook explains how to use `E2E-REFERENCE-SYSTEM-TRACK-00`.

## What The Track Does

The track creates bounded authority for building one coherent local Eureka
reference system. It pre-creates child packets so deterministic internal work
can proceed under shared hard gates.

The next task is:

```text
E2E-REFERENCE-CONTRACT-00
```

## Preflight

Before each child task, run:

```powershell
git fetch origin
git status --short --branch
git rev-list --left-right --count origin/main...origin/dev

python scripts/check_git_task_state.py `
  --mode start-task `
  --task-id <TASK-ID>
```

A `dev` branch-name warning is non-material when all other checks pass.

## Child Packets

The track pre-creates packets for:

```text
E2E-REFERENCE-CONTRACT-00
E2E-REFERENCE-RUNNER-00
E2E-PREVIEW-INDEX-00
E2E-HUNT-EXPLORATION-UI-00
SYNTHETIC-TRUTH-PATH-E2E-00
AUTONOMOUS-EVAL-ORACLE-00
PORTABLE-EUREKA-INSTANCE-00
HUMAN-END-TO-END-ACCEPTANCE-00
```

Current AIDE does not provide native inherited track authority. Each packet
therefore explicitly references `E2E-REFERENCE-SYSTEM-TRACK-00` and repeats the
relevant hard gates.

## Generated Output Locations

Track-level audit:

```text
control/audits/e2e-reference-system-track-00-v0/
```

Future child tasks should use task-specific subdirectories under:

```text
control/audits/e2e_reference_system/
.eureka/e2e-reference/
.eureka/test/e2e-reference/
```

Generated `.eureka` outputs should respect repo ignore policy and should not be
force-added unless a child task explicitly authorizes tracked generated output.

## Separate Authority Still Required

Stop and create a separate authority task before:

- enabling a new live provider or network path;
- using credentials or secrets;
- recording real Review Ledger decisions;
- materializing real reviewed records;
- mutating reviewed/master or public indexes;
- publishing public snapshots;
- exposing public services;
- downloading file payloads;
- installing, emulating, or executing artifacts;
- changing license posture;
- performing destructive data migration;
- distributing native/mobile clients;
- replacing reference semantics with Rust.

## IA Review Packet

The current IA review packet is frozen. It remains:

```text
56 prepared candidates
8 request_more_evidence decisions
48 pending parent-batch items
0 promoted candidates
0 reviewed records
```

Do not resume routine real-candidate review until the coherent local reference
experience reaches human acceptance.

## Validation

For track authority and light docs/control changes, use:

```powershell
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
python scripts/validate_runtime_architecture_leakage.py --json
python scripts/validate_public_alpha_readonly.py
python scripts/validate_snapshot_relay.py
python scripts/eureka_test_select.py --changed --failed-first --json
git diff --check
```

Do not run full unittest discovery for this authority task. Full discovery is
reserved for promotion/nightly/manual gates.

## Rollback And Stop Conditions

Stop if a child task needs authority outside its packet, if validation reports
truth/public boundary weakening, or if generated outputs imply reviewed truth.

Rollback of this track is a queue/control rollback only: restore the previous
queue recommendation and remove the child packets before beginning product
implementation under them.

