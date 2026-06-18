# Source Foundry Preview v0 Checkpoint

Task: `SOURCE-FOUNDRY-PREVIEW-V0-CHECKPOINT-00`

Status: `WAITING_FOR_EXTERNAL_FULL_DISCOVERY`

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

## Handoff

External full discovery is required before treating this checkpoint as promotion
ready. Use:

```powershell
python scripts/run_full_unittest_discovery.py --run-id source_foundry_preview_v0_checkpoint_00 --out ../eureka-test-runs/source_foundry_preview_v0_checkpoint_00 --quiet
python scripts/check_full_discovery.py --run-id source_foundry_preview_v0_checkpoint_00 --json
```

Return only the compact artifacts named in
`external_full_discovery_handoff.json`; do not paste raw unittest logs.
