# Source Foundry Preview v0 Checkpoint

Task: `SOURCE-FOUNDRY-PREVIEW-V0-CHECKPOINT-00`

Status: `BLOCKED_BY_EXTERNAL_FULL_DISCOVERY_FAILURE`

This checkpoint records the current `dev` Source Foundry Preview v0 milestone:

```text
IA metadata
-> source observations
-> candidates
-> evidence summaries
-> review batch
-> 8-item operator tranche
```

The milestone remains pending operator review. No IA candidate has become
reviewed truth.

## Boundary

- review decisions recorded: false
- review ledger written: false
- reviewed records created: false
- reviewed/master index mutated: false
- public index mutated: false
- snapshot refreshed: false
- public exposure changed: false
- external full discovery run inside AI session: false
- `dev -> main` promotion performed: false

## External Full Discovery Result

Run id: `source_foundry_preview_v0_checkpoint_00`

Status: `fail`

- latest run head: `f16d828714614c5ac7f84ab3e85aebc06cbf7a5d`
- latest run started: `2026-06-18T22:37:12Z`
- tests run: 5792
- failures: 43
- errors: 7
- failed tests: 50
- failed modules: 40
- failure families: 31

The compact result has now failed twice with the same substantive counts. The
latest compact result is recorded in `FULL_DISCOVERY_RESULT.md` and
`full_discovery_result.json`. `dev -> main` promotion remains blocked.

## Handoff

External full discovery has returned red. Do not promote `dev -> main` until a
repair or policy update produces a green compact full-discovery result. The
rerun command remains:

```powershell
python scripts/run_full_unittest_discovery.py --run-id source_foundry_preview_v0_checkpoint_00 --out ../eureka-test-runs/source_foundry_preview_v0_checkpoint_00 --quiet
python scripts/check_full_discovery.py --run-id source_foundry_preview_v0_checkpoint_00 --json
```

Return only the compact artifacts named in
`external_full_discovery_handoff.json`; do not paste raw unittest logs.
